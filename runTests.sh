#!/bin/bash

modelFile="examples/homeautomation.xml"
array=("1 100 20 .50" "2 100 50 .50" "3 100 75 .50" "4 100 100 .50" "5 100 150 .50" "6 100 200 .50" "7 100 100 .20" "8 100 100 .30" "9 100 100 .40" "10 100 100 .50" "11 100 100 .60" "12 100 100 .70" "13 100 100 .80" )

for config in "${array[@]}"; do
	python testOptimizers.py $modelFile $config
done