import os

import foyer
import pytest
import signac

from reproducibility_project.src import xmls
from reproducibility_project.tests.utils import create_gsd


class BaseTest:
    @pytest.fixture
    def spceff(self, name="spce.xml"):
        abs_path = os.path.dirname(os.path.abspath(xmls.__file__))
        return foyer.Forcefield(forcefield_files=str(abs_path) + "/" + name)

    @pytest.fixture
    def job_gsdfile(self, tmp_job):
        filename = tmp_job.fn("trajectory.gsd")
        create_gsd(filename)
        return tmp_job

    @pytest.fixture
    def tmp_project(self):
        with signac.TemporaryProject(name="test") as p:
            return p

    @pytest.fixture
    def tmp_job(self, tmp_project, statepoint={"a": 0}):
        tmp_project.open_job(statepoint).init()
        for job in tmp_project:
            return job

    @pytest.fixture
    def trappe_ua(self):
        return foyer.forcefields.load_TRAPPE_UA()

    @pytest.fixture
    def gsdfile_random(self, tmp_path):
        filename = tmp_path / "traj_random.gsd"
        create_gsd(filename)
        return filename

    @pytest.fixture
    def gsdfile_xstal(self, tmp_path):
        filename = tmp_path / "traj_xstal.gsd"
        create_gsd(filename, system="xstal")
        return filename

    @pytest.fixture
    def mock_job_npt(self):
        job_sp = {
            "molecule": "pentaneUA",
            "engine": "gromacs",
            "replica": 1,
            "temperature": 372,
            "pressure": 1402.0,
            "ensemble": "NPT",
            "N_liquid": 100,
            "N_vap": None,
            "box_L_liq": 4.055,
            "box_L_vap": None,
            "init_liq_den": 0.5390,
            "init_vap_den": None,
            "mass": 72.15,
            "forcefield_name": "Trappe_UA",
            "cutoff_style": "hard",
            "r_cut": 0.14,
        }
        return job_sp

    @pytest.fixture
    def mock_job_gemc(self):
        job_sp = {
            "molecule": "pentaneUA",
            "engine": "gromacs",
            "replica": 1,
            "temperature": 372,
            "pressure": 1402.0,
            "ensemble": "GEMC",
            "N_liquid": 300,
            "N_vap": 100,
            "box_L_liq": 4.055,
            "box_L_vap": 8.575,
            "init_liq_den": 0.5390,
            "init_vap_den": 0.019,
            "mass": 72.15,
            "forcefield_name": "Trappe_UA",
            "cutoff_style": "hard",
            "r_cut": 0.14,
        }
        return job_sp
