def modify_script(filename,line,content):
    with open(filename, "r") as f:
        lines = f.readlines()
        lines[line] = content
    with open(filename, "w") as f:
        f.writelines(lines)
    return

import signac
import os
p = signac.get_project()
for j in p.find_jobs({"engine":"lammps-UD","molecule":"waterSPCE"}):
    #modify_script(j.fn('submit.slurm'),4,"#SBATCH --time=01:59:59\n")
    #modify_script(j.fn('in.production-npt'),44,"run ${runtime} upto\n")
    os.remove(j.fn('eqlog0.txt'))
 

