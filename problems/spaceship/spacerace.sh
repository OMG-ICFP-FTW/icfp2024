#!/bin/bash

# iterate over levels 1 through 25 inclusive

# iterate over max_speeds 1 through 50 inclusive

timeout=1000

for max_speed in {1..5}
do
    echo "speed set to $max_speed"
    for i in {19..19}
    do
        echo "level $i speed $max_speed timeout $timeout"
        for choices in {1..10}
        do
            ./spaceship.py -l level${i}.txt -o solution${i}.txt -m $max_speed -t $timeout -c $choices
        done
    done
done