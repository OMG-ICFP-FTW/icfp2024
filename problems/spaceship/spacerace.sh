#!/bin/bash

# iterate over levels 1 through 25 inclusive

# iterate over max_speeds 1 through 50 inclusive

timeout=15

for i in {5..9}
do
    echo "Solving level $i"
    for max_speed in {1..50}
    do
        ./spaceship.py -l level${i}.txt -o solution${i}.txt -m $max_speed -t $timeout
    done
done