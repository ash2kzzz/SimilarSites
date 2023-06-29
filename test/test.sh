#! /usr/bin/bash

for file in `ls ../new_patch/`
do
    if [[ -d "../new_patch/"$file ]]
    then
        continue
    else
        python3 ../src/main.py -p "../new_patch/"$file >> result.txt
    fi
done