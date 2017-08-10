import os,sys

def load_file(file):
    """
    load the file and return the lines in this file.
    """
    try:
        with open(file) as f:
            lines = f.readlines()
    except:
        print('Could not open file!')
        raise
    return lines
def get_2d_rmsd(rmsd_file):
    lines = load_file(rmsd_file)
    rmsd_2d = []
    for line in lines[1:]:
        l = line.split()
        for i in l[1:]:
            if i == '0.000':
                break
            else:
                rmsd_2d.append(float(i))
    mean = sum(rmsd_2d)/len(rmsd_2d)
    stdev = (sum([(i-mean)**2 for i in rmsd_2d])/(len(rmsd_2d)-1))**0.5
    return rmsd_file, mean, stdev

if __name__=='__main__':
    if len(sys.argv) <2:
        print('Please provide a 2D RMSD data file!')
        sys.exit()
    else:
        print("%s:\t %.3f ± %.3f Å" %(get_2d_rmsd(sys.argv[1])))