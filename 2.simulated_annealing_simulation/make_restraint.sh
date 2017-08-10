#!/bin/bash
## define the name for the project
name="1"

#check necessary files for making restraint
if [ ! -f $name.pdb ];
then
        echo "ERROR: pdb file not found!"
        exit
fi

if [ ! -f map_added.DG-AMBER ];
then
        echo "ERROR: map_added.DG-AMBER not found!"
        exit
fi

if [ ! -f tordef.lib ];
then
        echo "ERROR: tordef.lib not found!"
        exit
fi

rm RST.dist

makeDIST_RST -ual noe.8col -pdb $name.pdb -map map_added.DG-AMBER -rst noe.dist
makeDIST_RST -ual hbond.8col -pdb $name.pdb -map map_added.DG-AMBER -rst hbond.dist
sed -i 's/ir6=1/ir6=0/g' noe.dist
sed -i 's/ir6=1/ir6=0/g' hbond.dist
makeANG_RST -pdb $name.pdb -con torsion.5col -lib tordef.lib >>torsion.dist
sed -i 's/rk2 =   2.0, rk3 =   2.0/rk2 =   200.0, rk3 =   200.0/g' torsion.dist
makeCHIR_RST $name.pdb chir.dist
sed -i 's/rk2 = 10., rk3=10./rk2 = 100., rk3 = 100./g' chir.dist
cat noe.dist hbond.dist torsion.dist planarity.dist chir.dist >>RST.dist
echo "Restraint file: RST.dist has been successfully created!"
