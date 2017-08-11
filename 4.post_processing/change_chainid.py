#!/usr/bin/env python



import sys

chainid = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N',\
        'O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c',\
        'd','e','f','g','h','i','j','k','l','m','n','o','p','q','r',\
        's','t','u','v','w','x','y','z','0','1','2','3','4','5','6',\
        '7','8','9']

def change_chain(pdb):
    new_pdb = 'new_'+pdb
    with open(pdb, 'r') as f:
        lines = f.readlines()
    with open(new_pdb, 'w') as fo:
        count = 0
        resi_shift = 0
        for line in lines:
            ter = line[:3]
            model = line[:5]
            if count >0 and ter == 'ATO':
                resi = int(line.split()[5])
                newline = line[:21]+chainid[count]+line[22:24]+(str(resi-resi_shift)).rjust(2) + line[26:]
            elif count >0 and ter == 'TER':
                resi = int(line.split()[-1])
                newline = line[:24]+(str(resi-resi_shift)).rjust(2) + line[26:]
            else:
                newline = line
    # if it's an ATOM line, sub the chainid
            if ter == 'TER':
                count += 1
                fo.write(newline)
                resi_shift = int(line.split()[-1])
            elif model == 'MODEL':
                fo.write(line)
                count = 0
                resi_shift = 0
            else:
                fo.write(newline)
        return new_pdb

if __name__=='__main__':
    if len(sys.argv) !=2:
        print('A pdb file must be provided. Existing...')
        sys.exit()
    new_pdb = change_chain(sys.argv[1])
    print('Successfully write pdb: %s' %new_pdb)
