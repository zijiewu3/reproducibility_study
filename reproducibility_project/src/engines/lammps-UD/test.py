fn = '../../../workspace/c55656e61236c29f43bf1d055946a467/box.lammps'
with open(fn,'r') as f:
    lines = f.readlines()
    print(lines[50:52])
    t = lines[50].split('\t')
    print(t)
    t[1] = str(1)
    print(t)
    lines[50] = '\t'.join(t)
    print(lines[50:52])
    #print(lines[1545:1547])
