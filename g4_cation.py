#!/usr/bin/env python
'''
Add cations to the center of 2 G-quartets. Using the average coordinates of O6 atom of guanine
base as the coordinates of cations. Deafult cation is K+.
Usage: python g_cation.py xxx.pdb  residue serial numbers in 1st G-quartet  2nd G-quaret...
eg: python g_cation.py xxx.pdb 1,2,3,4  5,6,7,8  9,10,11,12
in which the 1,2,3,4 are the residue serial numbers in 1st G-quartet
'''
__author__='Baifan Wang'
import os, sys
def pdb_loader(pdb):
    """load the pdb file and return the lines in pdb """
    try:
        with open(pdb) as f:
            lines = f.readlines()
    except:
        print('Could not open pdb file!')
        raise
    lines = [i for i in lines if not i.startswith('END')]
    return lines

def get_o6_average(pdb, quartet):
    lines = pdb_loader(pdb)
    coordinate=[]
    average = []
    for line in lines:
        if line.startswith('ATOM'):
            if line.split()[4] in quartet and line.split()[2]=='O6':
                coordinate.append([float(i) for i in line.split()[5:8]])
    average.append(sum(i[0] for i in coordinate)/len(coordinate))
    average.append(sum(i[1] for i in coordinate)/len(coordinate))
    average.append(sum(i[2] for i in coordinate)/len(coordinate))
    return average

def get_cation_line(pdb, average):
    lines = pdb_loader(pdb)
    i = -1
    while not lines[i].startswith('ATOM'):
        i-=1
    res_serial = int(lines[i].split()[4])+1
    atom_serial = int(lines[i].split()[1])+1
    character = 'ATOM'
    alter_local_indicater = ''
    code_for_insertions_of_residues = ''
    occupancy = 1.00
    temp_factor = 0.00
    segment_indent = ''
    element_symbol = 'K'
    charge = ''
    atom_name="  K+"
    res_name = 'K+'
    x = average[0]
    y = average[1]
    z = average[2]
    chain_id = ' '
    s = "%s%5d %s %3s %1s%4d%s    %8.3f%8.3f%8.3f%6.2f%6.2f      %4s%2s%2s" \
            % (character.ljust(6) , atom_serial , atom_name,  res_name.rjust(3) , \
            chain_id , res_serial , code_for_insertions_of_residues , \
            x , y , z , occupancy ,\
            temp_factor , segment_indent.ljust(4) , \
            element_symbol.rjust(2) , charge)
    return s

def write_new_pdb(pdb, cation_lines):
    old_lines = pdb_loader(pdb)
    with open(pdb,'w') as f:
        for line in old_lines:
            f.write(line)
        f.write('TER   \n')
        f.write(cation_line+'\n')

if __name__=='__main__':
    pdb = sys.argv[1]
    quartets = []
    if len(sys.argv)<4:
        print('Usage: python  g_cation.py  xx.pdb  1,2,3,4  5,6,7,8')
        sys.exit()

    for q in sys.argv[2:]:
        quartets.append([i for i in q.split(',')])
    for i in quartets:
        if len(i) != 4:
            print("Please put 4 residue serial number in a G-quartet join with ','")
            sys.exit()

    quartets = [quartets[i]+quartets[i+1] for i in range(len(quartets)-1)]
    for q in quartets:
        average = get_o6_average(pdb,q)
        cation_line = get_cation_line(pdb, average)
        write_new_pdb(pdb, cation_line)
    print('K+ ion(s) have been add to the following pdb: %s' %pdb)
