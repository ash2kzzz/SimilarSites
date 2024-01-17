#! /usr/bin/bash

#name="ground_truth"
#name="test"
#name="next_data"
name="true_positive"
folder="../$name\_patch"

for file in `ls $folder`
do
    if [[ -d $folder'/'$file ]]
    then
        continue
    else
        python3 ../src/main.py -p $folder'/'$file >> "../result/$name.txt"
    fi
done