#!/bin/bash
###specifiy which gpu to use(0 or 1)
export CUDA_VISIBLE_DEVICES=0

## define the name for the project
name="1"

# checks necessary files for md

if [ ! -f md.in ];
then
        echo "ERROR: md.in not found!"
        exit
fi

if [ ! -f $name.top ];
then
        echo "ERROR: $name.top not found!"
        exit
fi


#### perform serial MD, change the number in 'i<' section to set up how many runs will be performed.

for ((i=1; i<$1+1; i++))
do
rep=`printf "%03d" $i`
pmemd.cuda -O -i md.in -o $name.$rep.out -c $name.rst -r $name.$rep.rst -x mdcrd -p $name.top -ref $name.rst
ambpdb -p $name.top -c $name.$rep.rst > $name.$rep.pdb
done

####generated statics of the energy and violation
rm svionergy.txt
sviol2 d *.out >> sviold
sviol2 t *.out >> sviolt
senergy *.out >> senergy
cat sviold sviolt senergy >> svionergy.txt
rm sviold sviolt senergy
