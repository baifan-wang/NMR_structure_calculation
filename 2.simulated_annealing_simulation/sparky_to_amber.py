import re, os, sys

aa = {"A": "ALA",
 "R": "ARG",
 "N": "ASN",
 "D": "ASP",
 "B": "ASX",
 "C": "CYS",
 "E": "GLU",
 "Q": "GLN",
 "Z": "GLX",
 "G": "GLY",
 "H": "HIS",
 "I": "ILE",
 "L": "LEU",
 "K": "LYS",
 "M": "MET",
 "F": "PHE",
 "P": "PRO",
 "S": "SER",
 "T": "THR",
 "W": "TRP",
 "Y": "TYR",
 "V": "VAL" }

na = {'A':'DA',
'G':'DG',
'C':'DC',
'T':'DT'}

def load_file(file):
    """
    load the file and return the lines in this file.
    """
    try:
        with open(file) as f:
            lines = f.readlines()
    except:
        print('Could not open pdb file!')
        raise
    return lines

def sparky_convert(sparky):
    temp = []
    content = []
    lines = load_file(sparky)
    t = []
    # split the line using '-' and space
    for line in lines:
        temp.append(re.split(r'[-\s]', line))
    for i in temp:
        r1 = i[0][0]     #residue 1
        r1s = i[0][1]    #residue 1 serial
        r1a = i[0][2:]   #atom of residue 1
        lower = i[2]
        upper = i[3]
        if len(i[1]) == 1 or len(i[1]) == 2:
            r2 = r1
            r2s = r1s
            r2a = i[1]
        elif i[1][1].isnumeric() and i[1][2].isalpha():
            r2 = i[1][0]   #residue 2
            r2s = i[1][1]  #residue 1 serial
            r2a = i[1][2:] #atom of residue 2
        else:
            r2 = r1
            r2s = r1s
            r2a = i[1]
        content.append([r1s, r1, r1a, r2s, r2, r2a, lower, upper])
    return content


def to_amber(content, amber, moltype):
    if moltype == 'DNA':
        ab = na
    elif moltype == 'protein':
        ab = aa
    with open(amber,'w') as f:
        for i in content:
            s = ' '.join([i[0],ab[i[1]],i[2],i[3],ab[i[4]],i[5],i[6],i[7]])
            f.write(s+'\n')
if __name__=='__main__':
    if len(sys.argv) <3:
        print('Usage:')
        pritn('python sparky_to_amber.py  sparky_file  amber.8col DNA(or protein)')
        sys.exit()
    sparky = sys.argv[1]
    amber = sys.argv[2]
    if len(sys.argv)==4:
        mol_type = sys.argv[3]
    else:
        mol_type = 'DNA'
    s = sparky_convert(sparky)
    to_amber(s, amber,mol_type)




