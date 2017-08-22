This repository provides protocol and scripts for simulated annealing simulation for NMR structure calculation using [Amber](http://ambermd.org/). If you are unfamiliar with Amber, please check the [tutorial](http://ambermd.org/tutorials/).
## 1.1 Create initial structure. 
Here the initial strucutre are created by 'leap' programm in amber. All of the necessary files are located in [1.initial_structure_and_minimization](https://github.com/baifan-wang/NMR_structure_calculation/tree/master/1.initial_structure_and_minimization). The 'leap.in' is a script containing the commands to load force field parameters, create initial structure, save files, etc. The current 'leap.in' is designed for the DNA molecule using the 'ff-nucleic-OL15' force field (see http://fch.upol.cz/ff_ol/downloads.php for detail). One can download these force field in this repository('ff-nucleic-OL15.frcmod' and 'ff-nucleic-OL15.lib') or from  http://fch.upol.cz/ff_ol/downloads.php.    
First you need to edit 'leap.in', input the sequence of your structure in {} in this line: "aaa = sequence {DG5 DG DG DG3}".    
Then use the following command to create amber topology and coordinate as well as pdb file:    
```bash
tleap -f leap.in
```
check if '1.top', '1.crd' and '1.pdb' are created. Check the '1.pdb' using Chimera or pymol.

## 1.2 Minimization of initial structure.
The 'initial_min.in' is the input parameter file for running minimization using sander or pmemd in amber.
Minimize your initial structure using the following command:
```bash
pmemd.cuda -O -i initial_min.in -p 1.top -c 1.crd -r 1.rst -o min.out
```
Assuming you have the GPU-accelerated pmemd programm. Otherwise you can use 'sander', 'pmemd', 'sander.MPI' or 'pmemd.MPI'.
This minimization will create the minimized coordinate '1.rst'. You can convert it into pdb file using:
```bash
ambpdb -p 1.top -c 1.rst >1.pdb
```

## 2.1 Create restraints and perform simulated annealing simulation.
All of the files are located in [2.simulated_annealing_simulation](https://github.com/baifan-wang/NMR_structure_calculation/tree/master/2.simulated_annealing_simulation). Before proceed, copy the topology, pdb and restart files from first step into this directory.
### 2.2 Convert sparky list to amber 8col file.
The script 'sparky_to_amber.py' is used to convert sparky list into amber 8col file. Assuming you have already convert the NOE volume into distance restraint, which means you have the files with the following content:
```bash
Y4HN-D3HN	2.6	5
Y4HN-W5HN	2.6	5
```
Then the following command can be used to convert this file:
```python
python sparky_to_amber.py sparky.list noe.8col protein
```
if your molecule is DNA, just replace 'protein' with 'DNA'
### 2.3 Make restraints
The NMR restraints file using in structure calculation are created by script: [make_restraint.sh]( https://github.com/baifan-wang/computational_chemistry_tools/blob/master/NMR_structure_calculation/make_restraint.sh). The restraints include NOE and hydrogen bond distance restraints as well as torsion angle restraints, planarity restraints (optional) and chirality restraints. The final restraint file created by this script is ‘RST.dist’. Usage:    
```bash
bash make_restraint.sh    
```
Assuming you already have the following files:    
* 1.pdb: pdb file for you initial structure. If you have different file name, change it in script.    
* noe.8col : NOE 8 column restraint file     
* hbond.8col: hydrogen bond 8 column restraint file     
* torsion.5col: torsion 5 column restraint file    
* planarity.dist: planarity restraint file (optional, you need to manually edit it or create a new one using [makePLANAR_RST.py](https://github.com/baifan-wang/computational_chemistry_tools/tree/master/Amber))    
* map_added.DG-AMBER: MAP file for creating NOE and hydrogen bond restraint    
* tordef.lib: library file for creating torsion restraint    
The ‘map_added.DG-AMBER’ and ‘tordef.lib’ can be found in this repositoriy, as well as examples for the ‘noe.8col’, ‘hbond.8col’, ‘torsion.5col’ and ‘planarity.dist’.    

#### [makePLANAR_RST.py](https://github.com/baifan-wang/computational_chemistry_tools/blob/master/Amber/makePLANAR_RST.py): Generate the planarity restraint for the input base pair to be used in Amber NMR calculation.    
Usage: 
```python
python makePLANAR_RST.py -i input_file -o output_file -res basepairs
python makePLANAR_RST.py -i wc.txt -o wc.dist      #read base pair definitation from wc.txt and output restraint to wc.dist
python makePLANAR_RST.py -res A 1 T 2 -o wc.dist   #read base pair definitation from input and output restraint to wc.dist
python makePLANAR_RST.py -res A 1 T 2 -i wc.txt -o wc.dist   #read base pair definitation from both input and wc.txt output restraint to wc.dist
python makePLANAR_RST.py -res A 1 T 2  #direct print the output 
```
-res: input residues type for base pair, eg: G 1 G 2 G 3    
input_file: base pair planarity definition file, eg:    
T 1 A 2    
T 2 A 3    
...

### 2.4 Perform simulated annealing simulation
The 'md.in' is the input parameter file for running simulated annealing (SA) simulation using NMR restraints.
The 'runmd.sh' is a script for running a batch SA simulation, asumming you have the amber topology and restart file '1.top' and '1.rst'. If you have different file name, edit the name="1"  line in ths script. You can set up, e.g., 100 SA simulation like this:
```bash
bash runmd.sh 100
```
After finished, 100 pdb files will be generated. Their energy, NMR restraint violation will be written in file ends with '.out', and statistics information will be presented in 'svionergy.txt'.

### 2.5 Get NMR violation from SA output file.
The "mdout_parser.py" is a python script to extract NMR violation and energy information form SA out put file. It can show the structures within a specified distance and torsion angle violation cutoff. For example, one can see which structures has distance violation less than 0.2 and torsion angle violation less than 5 degree by using the follwing command:
```python
python3 ../mdout_parser.py -d ../2.simulated_annealing_simulation -r -dist 0.3 -ang 2.5
```
will print the md out with distance violation less than 0.3 angstrom and torsion angle volation less than 2.5 degree, in which the top is the structure with minimum energy:
```bash
md out	max distance violation	max torsion violation	Energy
1.176.out	0.244	2.373	-5349.663
1.200.out	0.212	2.124	-5346.602
1.163.out	0.196	2.161	-5345.7317
1.007.out	0.253	1.630	-5344.5039
1.183.out	0.232	1.887	-5344.4069
1.124.out	0.255	1.966	-5344.3604
```

The options of 
'-d': the directory contains md output files.
'-r': print the results.
'-s': get statistics information. see 4th section.
'-dist': NMR violation distance cutoff, in angstrom.
'ang': NMR violation torsion angle cutoff, in degree.

## 3. Minimization
The simulated annealing calculation already contains the stage of cooling the structure to 0 K, which is a kind of minimization. But if you structures contain ill-defined parts (due to lack of NOEs), or you wish to do minimization using different or no restraint, you can do another minimization using the script "runmin.sh" and "min.in".
First you need to copy the topology and restraint file into the folder of "3.minimization", and then performed:
```bash
./runmin.sh 100
```
will do 10000 steps minimization for the 100 structures.
After finished, you can check the violation and energy of using "mdou_parser.py".

## 4. Preparation of PDB file and generation of NMR statistics
The "4.post_processing" folder contains script to prepare pdb file and get NMR statistics. Copy the topology file and the restart files of the 10 (or more) best structures which you selected, as well as restraint files into this folder.
### 4.1 Generate pdb files. 
After selecttion of 10 best structures, the script of "group_pdb.in" can put these strcutures into a single PDB file, which is the prerequisite of submission to the PDB database. Here you can copy the restart files (files end with ".rst") of the 10 best structures in this folder. Then modified the "group_pdb.in", edit the topology filename in the 1st line to your topology file, and specify the residues used to superimpose the structure by editting the line of "rms first :2-21&!(@H=) mass". Then using the command: 
```bash
cpptraj -i group_pdb.in
```
to generate pdb. The pdb file contains 10 structures will be "final.pdb".

### 4.2 Fix the chain ID.
If your structure is dimer or tetramer, it is necessary to fix the chian id in the PDB files generated by Amber. The python script of "change_chainid.py", can be used for this purpose. Use the command:
```python
python change_chainid.py final.pdb
```
to get the new pdb. The new pdb will be "new_final.pdb".

### 4.3 Get RMSD values.
The "cpptraj-2d_rmsd.in" is a Amber script to generated RMSD values between structures. Modify the following lines:
```bash
rms2d :1,7-9,11-13,19-21,23-24&!(@H=) rmsout 2-G_quarts.2drmsd.dat 
rms2d :1-9,11-21,23-24&!(@H=) rmsout 3-G_quarts+5'.2drmsd.dat
```
change the residue serial number according to your structure. Add new line if neccesary.
and then using the command:
```bash
cpptraj -i cpptraj-2d_rmsd.in
```
to compute the RMSD data. The data files shoudl be "xxx.dat".
Another python script, "compute_2d_rmsd.py", will get the final RMSD data from data files. Use the following command to get the final RMSD data from all of the data files:
```bash
for name in *.dat;do python compute_2d_rmsd.py ${name};done
```

### 4.4 get NMR statistics
To get the NMR statistics, we need to perform another minimization with only 1 step. Using the following command:
```bash
for name in *.rst,do sander -O -i min.in -p 1.top -c ${name} -r restart -o ${name%.rst}.out;done
```
The "mdout_parser.py" can be use to extract the NMR statistics from the final 10 best structures. ISse the command to get NMR statistics:
```python
python3 ../mdout_parser.py -d ../4.post_processing -s -dist 0.3 -ang 5
```
Here the distance and torsion angle cutoff for the NMR violation is 0.3 angstrom and 5 degree.
The results will be printing like this:
```bash
Average distance violation: 	0.10580839895013133
Standard deviation of distance violation: 	0.035639493409260856
Maximum distance violation: 	0.248
Number of distance violation larger than cutoff of 0.3: 	0
Average angle violation: 	1.9322105263157896
Standard deviation of angle violation: 	0.3619237756015229
Maximum angle violation: 	2.748
Number of angle violation larger than cutoff: 5.0: 	0
RMS deviation from ideal bonds: 	0.01167
RMS deviation from ideal angles: 	2.4383
```

## Tips for structure calculation of G-quadruplex.
Folding of initial extend conformation into folded G-quadruplex using NMR restraints could be challenge for beginner. Usually the initial conformation will fold into a mess under restraints. I recommend to use several SA simulations to gradually fold the structure, in each SA simulation the restraints are gradually added. For example, in the first SA simulation, only torsion and chirality as well as hydrogen bond restraints in the center of strand were added, which should result in a hairpin like structure (see the figure below). Then in the second SA simulation, the hydrogen bond restraint between the center strand and the 5’ or 3’ strand can be added, which should form triplex-like structure, and then G-quadruplex. After the initial fold of G-quadruplex was obtained, the NOE restraints can be gradually added. I suggest to add intra-residue NOE restraints first, and then check the violation and correct the wrong NOE restraints. Then repeat the calculation with the sequential NOE restraints, and with the long-range NOE restraints, and finally do the calculation to produce 100 structurs (or more if necessary).
![img](https://raw.githubusercontent.com/baifan-wang/NMR_structure_calculation/master/tip.jpg)


## [g4_cation.py](https://github.com/baifan-wang/computational_chemistry_tools/blob/master/g4_cation.py): Add cation to the center of 2 G-quartets. 
Using the average coordinates of O6 atom of guanine base as the coordinates of cations. Deafult cation is K+.
Usage: 
```python
python g_cation.py xxx.pdb  residue_serial_numbers_of 1st_G-quartet 2nd_G-quaret
```
eg: python g_cation.py xxx.pdb 1,2,3,4  5,6,7,8  9,10,11,12    
in which the 1,2,3,4 are the residue serial numbers in 1st G-quartet. The cations will be added to the center of G-quartet 1-2-3-4 and 5-6-7-8 as well as the center of G-quartet 5-6-7-8 and 9-10-11-12
