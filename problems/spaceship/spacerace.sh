#!/bin/bash

# iterate over levels 1 through 25 inclusive

# iterate over max_speeds 1 through 50 inclusive

timeout=15

for max_speed in {10..20}
do
    echo "speed set to $max_speed"
    for i in {14..18}
    do
        echo "level $i speed $max_speed timeout $timeout"
        for choices in {1..1}
        do
            ./spaceship.py -l level${i}.txt -o solution${i}.txt -m $max_speed -t $timeout -c $choices
        done
    done
done