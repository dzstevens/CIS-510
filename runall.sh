#!/bin/bash
MODELS=models/*
declare -a heuristics=(min-neighbor min-weights min-fill weighted-min-fill)
for f in $MODELS
do
    echo $f
    echo
    echo 'no heuristic:'
    python -m pgm.main $f partition_function -t
    for h in ${heuristics[@]}
    do
        echo $h
        python -m pgm.main $f partition_function -u $h -t
    done
    echo
done
