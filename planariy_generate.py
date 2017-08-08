#!/bin/env python3
import sys
def write_planaritets(r1, r2, r3, r4, filename):
    title = '''#  Plan Restraint: %s->%s->%s->%s ''' %(r1,r2,r3,r4)
    residue = [r1, r2, r3, r4, r1]
    with open (filename, 'w') as f:
        f.write(title+'\n')
        for i in range(4):
            comment = '''# %s->%s''' %(residue[i], residue[i+1])
            f.write(comment + '\n')
            content = '''#  planaritets restraint:  N9 N7 N1 N3
 &rst iat=%s,%s,%s,%s, atnam(1)='N9', atnam(2)='N7',
     atnam(3)='N1', atnam(4)='N3',
     r1=350.0, r2=355.0, r3=365.0, r4=370.0,
     rk2=20.0, rk3=20.0, nstep1=0, nstep2=200000, iresid=1, &end

#  planaritets restraint:  C5 C2 N7 C4
 &rst iat=%s,%s,%s,%s, atnam(1)='C5', atnam(2)='C2',
     atnam(3)='N7', atnam(4)='C4',
     r1=350.0, r2=355.0, r3=365.0, r4=370.0, iresid=1, &end

#  planaritets restraint:  C2 C8 C2 C8
 &rst iat=%s,%s,%s,%s, atnam(1)='C2', atnam(2)='C8',
     atnam(3)='C2', atnam(4)='C8',
     r1=350.0, r2=355.0, r3=365.0, r4=370.0,
      iresid=1, &end''' %(residue[i], residue[i], residue[i+1], residue[i+1],\
       residue[i], residue[i], residue[i+1], residue[i+1],\
        residue[i], residue[i], residue[i+1], residue[i+1])
            f.write(content+'\n')
if __name__=='__main__':
    r1 = sys.argv[1]
    r2 = sys.argv[2]
    r3 = sys.argv[3]
    r4 = sys.argv[4]
    filename = sys.argv[5]
    write_planaritets(r1, r2, r3, r4, filename)
