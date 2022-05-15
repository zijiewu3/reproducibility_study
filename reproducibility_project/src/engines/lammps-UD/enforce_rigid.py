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
def enforce_rigid(j,noapm):
    
    topo_path = j.fn('box.lammps')
    with open(topo_path,'r') as f:
        lines = f.readlines()
        for li, l in enumerate(lines):
            if l == 'Atoms # full\n':
                line_start = li+2
            if l == 'Bonds\n':
                line_end = li-1
                break
        curr_line = line_start
        apm_count = 0
        mol_count = 1
        while (curr_line < line_end):
            t = lines[curr_line].split('\t')
            t[1] = str(mol_count)
            lines[curr_line] = '\t'.join(t)
            apm_count += 1
            if apm_count == noapm:
                apm_count = 0
                mol_count += 1
            curr_line += 1
    with open(topo_path,"w") as f:
        f.writelines(lines)
            
    #modify_script(j.fn('submit.slurm'),4,"#SBATCH --time=01:59:59\n")
    #modify_script(j.fn('in.production-npt'),43,"run ${runtime} upto\n")  #TODO: Look to make sure this shift is okay

