#!/usr/bin/env python3
import os

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

class Mdout(object):
    def __init__(self,name):
        self.abs_name = name
        self.name     = os.path.split(name)[1]        #mdout file name
        self.energy   = []          #potential energy, average, rms
        self.dis_viol = []        #distance violation
        self.tor_viol = []        #torsion angle violation
        self.rms_b    = None        #RMS deviation from ideal bonds
        self.rms_a    = None        #RMS deviation from ideal angles
        self.imin = False
    def process_mdout(self):
        self.nstep = 'None'
        lines = load_file(self.abs_name)
        energy_flag = False
        viol_falg = False
        for line in lines:
            l = line.split()
            if l:
                if l[0] == 'imin' and l[2] == '1,':
                    self.imin = True
                elif l[0] == 'maxcyc' or l[0] == 'nstlim':  # to figure out how many steps of the simulatipn
                    self.nstep = l[2].strip(',')

                elif self.imin == True and l[0] == self.nstep: # if this is a minimization out put file
                        self.energy.append(float(l[1]))

                elif self.imin == False and energy_flag == True: # if this is a md out put file
                    self.energy.append(float(l[2]))
                    energy_flag = False
                elif self.imin == False and l[0] == 'NSTEP' and l[2] == self.nstep:
                     energy_flag = True

                elif line.endswith('0: 0\n'):
                    self.dis_viol.append([' '.join(l[0:3]),' '.join(l[4:7]),\
                        float(l[8]),float(l[9])])
                elif line.endswith(' t\n'):
                    self.tor_viol.append([' '.join(l[0:3]),' '.join(l[4:7]),\
                        float(l[8]),float(l[9])])
                elif line.startswith('|                               RMS deviation from ideal bonds'):
                    self.rms_b = float(l[-1])
                elif line.startswith('|                               RMS deviation from ideal angles'):
                    self.rms_a = float(l[-1])

    def _process_viol(self, viols):
        max_viol = 0
        sum_viol = 0
        for i in viols:
            viol = i[3]
            sum_viol += viol
            if max_viol <viol:
                max_viol = viol
        if len(viols) !=0:
            ave_viols = sum_viol/len(viols)
        else:
            ave_viols = 0
        return max_viol, ave_viols, sum_viol, len(viols)

    def get_dis_tor_max_viol(self):
        self.dis_viols = self._process_viol(self.dis_viol)
        self.tor_viols = self._process_viol(self.tor_viol)
        self.max_dis_viol = self.dis_viols[0]
        self.max_tor_viol = self.tor_viols[0]

    def run(self):
        self.process_mdout()
        self.get_dis_tor_max_viol()

    def is_not_empty(self):
        if len(self.energy) >= 1:
            return True
        else:
            return False

def get_all_mdout_files(directory):
    fe = '.out'  #file extension
    return sorted([os.path.join(directory,x) for x in os.listdir(directory) \
    if os.path.isfile(os.path.join(directory,x)) and os.path.splitext(x)[1]==fe])

def creat_mdout_obj(directory='.'):
    all_mdout_obj = []
    for f in get_all_mdout_files(directory):
        m = Mdout(f)
        m.run()
        all_mdout_obj.append(m)
    return all_mdout_obj

def filter_mdout_obj(all_mdout_obj, dis_cut_off, tor_cut_off):
    results = []
    for m in all_mdout_obj:
        if m.is_not_empty():
            if m.max_dis_viol <= dis_cut_off and m.max_tor_viol <= tor_cut_off:
                results.append(m)
    return sorted(results, key = lambda x: x.energy[0])

def get_results(directory='.', dis_cut_off=0.199, tor_cut_off=0):
    all_mdout_obj = creat_mdout_obj(directory)
    results = filter_mdout_obj(all_mdout_obj, dis_cut_off,tor_cut_off)
    return results

def get_ave_std_max(data):
    if len(data) > 0:
        mean = sum(data)/len(data)
        stdev = (sum([(i-mean)**2 for i in data])/(len(data)-1))**0.5
        max_ = max(data)
    elif len(data) == 0:
        mean = 0
        stdev = 0
        max_ = 0
    else:
        mean = data[0]
        stdev = 0
        max_ = data[0]
    return mean, stdev, max_
def get_statistics(all_mdout_obj, dis_cut_off, tor_cut_off):
    """ will compute the average violations and standard deviation, maximum violation,
        number of violation larger than cutoff"""
    all_dis_viol = []  # all of the distance violation
    all_tor_viol = []  # all of the torsion violation
    #put all of the violation together
    for m in all_mdout_obj:
        if len(m.dis_viol)>0:
            for i in m.dis_viol:
                all_dis_viol.append(i[3])
        if len(m.tor_viol)>0:
            for l in m.tor_viol:
                all_tor_viol.append(l[3])
    #compute average, standard deviation and maximum values of the violation
    ave_dis_viol, std_dis_viol, max_dis_viol = get_ave_std_max(all_dis_viol)
    ave_tor_viol, std_tor_viol, max_tor_viol = get_ave_std_max(all_tor_viol)
    #compute how many violation are larger than cutoff values.
    num_dis_viol = 0
    num_tor_viol = 0
    for i in all_dis_viol:
        if i >dis_cut_off:
            num_dis_viol += 1
    for l in all_tor_viol:
        if l >tor_cut_off:
            num_tor_viol += 1
    return ave_dis_viol, std_dis_viol, max_dis_viol, num_dis_viol, ave_tor_viol, std_tor_viol, max_tor_viol, num_tor_viol

def get_ideal_geometry(all_mdout_obj):
    ideal_bond = []
    ideal_angle = []
    for m in all_mdout_obj:
        if m.rms_b is not None:
            ideal_bond.append(m.rms_b)
        if m.rms_a is not None:
            ideal_angle.append(m.rms_a)
    bond_ave, bond_std, _ = get_ave_std_max(ideal_bond)
    angle_ave, angle_std, _ = get_ave_std_max(ideal_angle)
    return bond_ave, bond_std, angle_ave, angle_std


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='''Perform data analysis for NMR calculation.''')
    parser.add_argument('-d', '--directory', default='.', help='The folder contains MD output.')
    parser.add_argument('-r', '--result', action="store_true", help='print the summary results.')
    parser.add_argument('-s', dest='statistics', action="store_true", help='print the statistics results.')
    parser.add_argument('-dist', type=float,
                    dest='dist_cutoff', help='The NMR violation distance cutoff')
    parser.add_argument('-ang', type=float,
                    dest='angle_cutoff', help='The NMR violation angle cutoff')

    args = parser.parse_args()

    if args.result:
        results = get_results(args.directory, args.dist_cutoff, args.angle_cutoff)
        print("md out", "max distance violation", "max torsion violation", "Energy", sep = '\t')
        for m in results:
            print(m.name, m.max_dis_viol, m.max_tor_viol, m.energy[0], sep = '\t')
    if args.statistics:
        results = get_results(args.directory, dis_cut_off=1.0, tor_cut_off=180)
        data = get_statistics(results, args.dist_cutoff, args.angle_cutoff)
        items = ["Average distance violation", "Standard deviation of distance violation",\
        "Maximum distance violation","Number of distance violation larger than cutoff of %s" %args.dist_cutoff,\
        "Average torsion angle violation", "Standard deviation of angle violation",\
        "Maximum torsion angle violation","Number of torsion angle violation larger than cutoff: %s" %args.angle_cutoff]
        for i,l in zip(items, data):
            print(i,l, sep = ': \t')
        ideal_data = get_ideal_geometry(results)
        print("RMS deviation from ideal bonds", ideal_data[0], sep = ': \t')
        print("RMS deviation from ideal angles", ideal_data[2], sep = ': \t')