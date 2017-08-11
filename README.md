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
### Convert sparky list to amber 8col file.
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
### Make restraints
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

## [makePLANAR_RST.py](https://github.com/baifan-wang/computational_chemistry_tools/blob/master/Amber/makePLANAR_RST.py): Generate the planarity restraint for the input base pair to be used in Amber NMR calculation.    
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

## 2.2 Perform simulated annealing simulation
The 'md.in' is the input parameter file for running simulated annealing (SA) simulation using NMR restraints.
The 'runmd.sh' is a script for running a batch SA simulation, asumming you have the amber topology and restart file '1.top' and '1.rst'. If you have different file name, edit the name="1"  line in ths script. You can set up, e.g., 100 SA simulation like this:
```bash
bash runmd.sh 100
```
After finished, 100 pdb files will be generated. Their energy, NMR restraint violation will be written in file ends with '.out', and statistics information will be presented in 'svionergy.txt'.

## 3. Minimization

## 4. Get NMR stastics and preperation of PDB files.

## Tips for structure calculation of G-quadruplex.
Folding of initial extend conformation into folded G-quadruplex using NMR restraints could be challenge for beginner. Usually the initial conformation will fold into a mess under restraints. I recommend to use several SA simulations to gradually fold the structure, in each SA simulation the restraints are gradually added. For example, in the first SA simulation, only torsion and chirality as well as hydrogen bond restraints in the center of strand were added, which should result in a hairpin like structure (see the figure below). Then in the second SA simulation, the hydrogen bond restraint between the center strand and the 5’ or 3’ strand can be added, which should form triplex-like structure, and then G-quadruplex. After the initial fold of G-quadruplex was obtained, the NOE restraints can be gradually added. I suggest to add intra-residue NOE restraints first, and then check the violation and correct the wrong NOE restraints. Then repeat the calculation with the sequential NOE restraints, and with the long-range NOE restraints, and finally do the calculation to produce 100 structurs (or more if necessary).
![img](https://raw.githubusercontent.com/baifan-wang/NMR_structure_calculation/master/tip.jpg)

