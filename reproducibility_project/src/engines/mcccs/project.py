"""Setup for signac, signac-flow, signac-dashboard for this study."""
# import foyer
import fileinput
import os
import pathlib
import shutil
from glob import glob

import flow
from flow import FlowProject, environments


class Project(flow.FlowProject):
    """Subclass of FlowProject to provide custom methods and attributes."""

    def __init__(self):
        super().__init__()
        current_path = pathlib.Path(os.getcwd()).absolute()
        self.data_dir = current_path.parents[1] / "data"
        self.ff_fn = self.data_dir / "forcefield.xml"


ex = Project.make_group(name="ex")


def get_system(job):
    """Return the system (mbuild filled_box) for a particular job."""
    molecule = job.sp.molecule
    import warnings

    import mbuild as mb

    from reproducibility_project.src.utils.forcefields import load_ff

    warnings.simplefilter("ignore")
    methane = mb.Compound(name="MET")
    methane_child_bead = mb.Compound(name="_CH4")
    methane.add(methane_child_bead, inherit_periodicity=False)
    box_liq = mb.fill_box(
        compound=methane, n_compounds=1230, box=[4.5, 4.5, 4.5]
    )
    ff = load_ff(job.sp.forcefield_name)
    parameterized_box_liquid = ff.apply(box_liq)
    return box_liq


def get_molecules(job):
    """Return the list of mbuild molecules being used in the job."""
    molecule = job.sp.molecule
    import warnings

    import foyer
    import mbuild as mb

    warnings.simplefilter("ignore")
    methane = mb.Compound(name="MET")
    methane_child_bead = mb.Compound(name="_CH4")
    methane.add(methane_child_bead, inherit_periodicity=False)
    return [methane]


@Project.label
def has_fort_files(job):
    """Check if the job has all four equired fort.4 files."""
    return (
        job.isfile("fort.4.melt")
        and job.isfile("fort.4.cool")
        and job.isfile("fort.4.equil")
        and job.isfile("fort.4.prod")
    )


@Project.label
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
def files_ready(job):
    """Check if the keywords in the fort.4 files have been replaced."""
    # Link: https://stackoverflow.com/questions/32749350/check-if-a-string-is-in-a-file-with-python
    job.doc.files_ready = False
    file_names = ["melt", "cool", "equil", "prod"]
    print(job.ws)
    keywords = ["NCHAIN", "LENGTH", "TEMPERATURE", "PRESSURE", "VARIABLES"]
    c = 0
    for name in file_names:
        file_name = job.ws + "/fort.4." + name
        i = 0
        for i in range(len(keywords)):
            with open(file_name) as myfile:
                if keywords[i] in myfile.read():
                    c += 1
    if c == 0:
        job.doc.files_ready = True

    return job.doc.files_ready


@Project.label
def has_restart_file(job):
    """Check if the job has a restart file."""
    return job.isfile("fort.77")


@Project.label
def has_topmon(job):
    """Check if the job has a topmon (FF) file."""
    return job.isfile("topmon.inp")


@Project.label
def has_fort77maker(job):
    """Check if the job has a fort77maker file (obsolete)."""
    return os.path.isfile(
        Project().root_directory()
        + "/src/engines/mcccs/"
        + "fort77maker_onebox.py"
    )


@Project.label
def replicate_set(job):
    """Check if number of replicates for prod has been set."""
    try:
        return job.doc.num_prod_replicates == 4
    except AttributeError:
        return False


@Project.label
def all_prod_replicates_done(job):
    """Check if all prod replicate simulations completed."""
    try:

        return job.doc.prod_replicates_done >= job.doc.num_prod_replicates
    except AttributeError:
        return False


@Project.label
def melt_finished(job):
    """Check if melt stage is finished."""
    step = "melt"
    run_file = job.ws + "/run.{}".format(step)
    if job.isfile("run.{}".format(step)):
        with open(run_file) as myfile:
            if "Program ended" in myfile.read():
                return True
            else:
                return False


@Project.label
def cool_finished(job):
    """Check if cool stage is finished."""
    step = "cool"
    run_file = job.ws + "/run.{}".format(step)
    if job.isfile("run.{}".format(step)):
        with open(run_file) as myfile:
            if "Program ended" in myfile.read():
                return True
            else:
                return False


@Project.label
def equil_finished(job):
    """Check if equil stage is finished."""
    step = "equil"
    run_file = job.ws + "/run.{}".format(step)
    if job.isfile("run.{}".format(step)):
        with open(run_file) as myfile:
            if "Program ended" in myfile.read():
                return True
            else:
                return False


@Project.label
def prod_finished(job):
    """Check if prod stage is finished."""
    step = "prod" + str(job.doc.prod_replicates_done)
    run_file = job.ws + "/run.{}".format(step)
    if job.isfile("run.{}".format(step)):
        with open(run_file) as myfile:
            if "Program ended" in myfile.read():
                return True
            else:
                return False


@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.post(replicate_set)
def set_prod_replicates(job):
    """Copy the files for simulation from engine_input folder."""
    job.doc.num_prod_replicates = 4
    job.doc.prod_replicates_done = 0


@ex
@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.post(has_fort_files)
def copy_files(job):
    """Copy the files for simulation from engine_input folder."""
    for file in glob(
        Project().root_directory()
        + "/src/engine_input/mcccs/{}/fort.4.*".format(job.sp.molecule)
    ):
        shutil.copy(file, job.workspace() + "/")


@ex
@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.post(has_fort77maker)
def copy_fort77maker(job):
    """Copy fort77maker_onebox.py from root directory to mcccs directory."""
    shutil.copy(
        Project().root_directory()
        + "/src/engine_input/mcccs/fort77maker_onebox.py",
        Project().root_directory() + "/src/engines/mcccs/",
    )


@ex
@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.post(has_topmon)
def copy_topmon(job):
    """Copy topmon.inp from root directory to mcccs directory."""
    shutil.copy(
        Project().root_directory()
        + "/src/engine_input/mcccs/{}/topmon.inp".format(job.sp.molecule),
        job.workspace() + "/",
    )


@ex
@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.pre(has_fort_files)
@Project.post(files_ready)
def replace_keyword_fort_files(job):
    """Replace keywords with the values of the variables defined in signac statepoint."""
    file_names = ["melt", "cool", "equil", "prod"]
    seed = job.sp.replica
    nchain = 1230
    length = 45
    temperature = 100
    pressure = 10
    variables = [nchain, length, temperature, pressure, seed]
    keywords = ["NCHAIN", "LENGTH", "TEMPERATURE", "PRESSURE", "SEED"]
    for name in file_names:
        file_name = job.ws + "/fort.4." + name
        i = 0
        for i in range(len(variables)):
            with fileinput.FileInput(file_name, inplace=True) as file:
                for line in file:
                    print(line.replace(keywords[i], str(variables[i])), end="")


@ex
@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.pre(has_fort77maker)
@Project.post(has_restart_file)
def make_restart_file(job):
    """Make a fort77 file for the job."""
    from fort77maker_onebox import fort77writer

    molecules = get_molecules(job)
    filled_box = get_system(job)

    fort77writer(
        molecules,
        filled_box,
        output_file=job.ws + "/fort.77",
        xyz_file=job.ws + "/initial_structure.xyz",
    )


@ex
@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.pre(has_restart_file)
@Project.pre(has_fort_files)
@Project.pre(has_topmon)
@Project.pre(files_ready)
@Project.post(melt_finished)
def run_melt(job):
    """Run melting stage."""
    from subprocess import PIPE, Popen

    step = "melt"
    """Run the melting stage."""
    print("Running {}".format(step))
    execommand = "/home/rs/group-code/MCCCS-MN-7-20/exe-8-20/src/topmon"
    os.chdir(job.ws)
    shutil.copyfile("fort.4.{}".format(step), "fort.4")
    process = Popen(
        execommand,
        shell=True,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    output, error = process.communicate()
    print(output)
    shutil.move("fort.12", "fort.12.{}".format(step))
    shutil.move("box1config1a.xyz", "box1config1a.xyz.{}".format(step))
    shutil.move("run1a.dat", "run.{}".format(step))
    shutil.copy("config1a.dat", "fort.77")
    shutil.move("config1a.dat", "config1a.dat.{}".format(step))
    shutil.move("box1movie1a.pdb", "box1movie1a.pdb.{}".format(step))
    shutil.move("box1movie1a.xyz", "box1movie1a.xyz.{}".format(step))


@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.pre(has_restart_file)
@Project.pre(melt_finished)
@Project.post(cool_finished)
def run_cool(job):
    """Run cool stage."""
    from subprocess import PIPE, Popen

    step = "cool"
    """Run the melting stage."""
    print("Running {}".format(step))
    execommand = "/home/rs/group-code/MCCCS-MN-7-20/exe-8-20/src/topmon"
    os.chdir(job.ws)
    shutil.copyfile("fort.4.{}".format(step), "fort.4")
    process = Popen(
        execommand,
        shell=True,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    output, error = process.communicate()
    print(output)
    shutil.move("fort.12", "fort.12.{}".format(step))
    shutil.move("box1config1a.xyz", "box1config1a.xyz.{}".format(step))
    shutil.move("run1a.dat", "run.{}".format(step))
    shutil.copy("config1a.dat", "fort.77")
    shutil.move("config1a.dat", "config1a.dat.{}".format(step))
    shutil.move("box1movie1a.pdb", "box1movie1a.pdb.{}".format(step))
    shutil.move("box1movie1a.xyz", "box1movie1a.xyz.{}".format(step))


@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.pre(has_restart_file)
@Project.pre(cool_finished)
@Project.post(equil_finished)
def run_equil(job):
    """Run equilibration."""
    from subprocess import PIPE, Popen

    step = "equil"
    """Run the melting stage."""
    print("Running {}".format(step))
    execommand = "/home/rs/group-code/MCCCS-MN-7-20/exe-8-20/src/topmon"
    os.chdir(job.ws)
    shutil.copyfile("fort.4.{}".format(step), "fort.4")
    process = Popen(
        execommand,
        shell=True,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    output, error = process.communicate()
    print(output)
    shutil.move("fort.12", "fort.12.{}".format(step))
    shutil.move("box1config1a.xyz", "box1config1a.xyz.{}".format(step))
    shutil.move("run1a.dat", "run.{}".format(step))
    shutil.copy("config1a.dat", "fort.77")
    shutil.move("config1a.dat", "config1a.dat.{}".format(step))
    shutil.move("box1movie1a.pdb", "box1movie1a.pdb.{}".format(step))
    shutil.move("box1movie1a.xyz", "box1movie1a.xyz.{}".format(step))


@Project.operation
@Project.pre(
    lambda j: j.sp.simulation_engine == "mcccs" and j.sp.molecule == "methane"
)
@Project.pre(has_restart_file)
@Project.pre(equil_finished)
@Project.post(prod_finished)
@Project.post(all_prod_replicates_done)
def run_prod(job):
    """Run production."""
    from subprocess import PIPE, Popen

    job.doc.prod_replicates_done += 1
    replicate = job.doc.prod_replicates_done
    step = "prod" + str(replicate)
    """Run the melting stage."""
    print("Running {}".format(step))
    execommand = "/home/rs/group-code/MCCCS-MN-8-21/exe-8-21/src/topmon"
    os.chdir(job.ws)
    shutil.copyfile("fort.4.prod", "fort.4")
    process = Popen(
        execommand,
        shell=True,
        universal_newlines=True,
        stdin=PIPE,
        stdout=PIPE,
        stderr=PIPE,
    )
    output, error = process.communicate()
    print(output)
    shutil.move("fort.12", "fort.12.{}".format(step))
    shutil.move("box1config1a.xyz", "box1config1a.xyz.{}".format(step))
    shutil.move("run1a.dat", "run.{}".format(step))
    shutil.copy("config1a.dat", "fort.77")
    shutil.move("config1a.dat", "config1a.dat.{}".format(step))
    shutil.move("box1movie1a.pdb", "box1movie1a.pdb.{}".format(step))
    shutil.move("box1movie1a.xyz", "box1movie1a.xyz.{}".format(step))
    print(job.doc.prod_replicates_done)
    print(all_prod_replicates_done(job))
    print(prod_finished(job))


if __name__ == "__main__":
    pr = Project()
    pr.main()
