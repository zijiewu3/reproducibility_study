import signac
import copy 

mc_engines = ("gomc", "mcccs", "cassandra")
md_engines = ("gromacs", "hoomd", "lammps-VU", "lammps-UD")

def update_MD_statepoints(project):
    for job in project:
        if job.sp.molecule == "pentaneUA" and job.sp.engine in md_engines:
            #print(job.id, job.sp)
            statepoint = copy.copy(job.sp)
            statepoint.pop("molecule")
            statepoint["molecule"] = "pentaneUA-flexible_bonds"
            job.update_statepoint(statepoint)
        
def update_MC_statepoints(project):
    for job in project:
        if job.sp.molecule == "pentaneUA" and job.sp.engine in mc_engines:
            #print(job.id, job.sp)
            statepoint = copy.copy(job.sp)
            statepoint.pop("molecule")
            statepoint["molecule"] = "pentaneUA-constrain_bonds"
            job.update_statepoint(statepoint)
  
def main():
    p = signac.get_project()
    print(p)
    print("Updating MD pentaneUA job name to pentaneUA-flexible_bonds")
    update_MD_statepoints(p)
    print("Updating MC pentaneUA job name to pentaneUA-constrain_bonds")
    update_MC_statepoints(p)
    


if __name__ == "__main__":
    main()
    
