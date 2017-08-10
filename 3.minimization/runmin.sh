#!/bin/bash
###specifiy which gpu to use(0 or 1)
export CUDA_VISIBLE_DEVICES=0

## define the name for the project
name="1"

# checks necessary files for md

if [ ! -f min.in ];
then
        echo "ERROR: min.in not found!"
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
pmemd.cuda -O -i md.in -o $name.$rep.min.out -c ../2.simulated_annealing_simulation/$name.$rep.rst -r $name.$rep.min.rst -x mdcrd -p $name.top -ref ../$name.$rep.rst
ambpdb -p $name.top -c $name.$rep.min.rst > $name.$rep.min.pdb
done

