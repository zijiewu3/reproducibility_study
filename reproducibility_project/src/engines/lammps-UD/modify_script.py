def modify_script(filename,line,content):
    with open(filename, "r") as f:
        lines = f.readlines()
        lines[line] = content
    with open(filename, "w") as f:
        f.writelines(lines)
    return

import signac
import os
from shutil import copyfile
p = signac.get_project()
for j in p.find_jobs({"engine":"lammps-UD","molecule":"benzeneUA"}):
    j.clear()
    #modify_script(j.fn('submit.slurm'),4,"#SBATCH --time=01:59:59\n")
    #modify_script(j.fn('in.production-npt'),43,"run ${runtime} upto\n")  #TODO: Look to make sure this shift is okay
    try:
        os.remove(j.fn('*.restart-*'))
    except Exception as e:
        pass
#    try:
#        os.remove(j.fn('production-npt.restart-1'))
#    except Exception as e:
#        pass
    try:
        os.remove(j.fn('*.txt'))
    except Exception as e:
        pass
    try:
        os.remove(j.fn('*.dcd'))
    except Exception as e:
        pass
    try:
        os.remove(j.fn('*log*'))
    except Exception as e:
        pass
    try:
        os.remove(j.fn('*log*'))
    except Exception as e:
        pass
    copyfile("../../engine_input/lammps/input_scripts/in.production-nvt",j.fn('in.production-nvt'))
    copyfile("../../engine_input/lammps/input_scripts/in.production-npt",j.fn('in.production-npt'))
    copyfile("../../engine_input/lammps/input_scripts/in.equilibration",j.fn('in.equilibration'))
    #os.listdir(j.fn(''))

