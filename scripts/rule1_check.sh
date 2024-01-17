#! /usr/bin/bash

echo "TEST ground truth dataset"
python3 ../src/main.py -p ../ground_truth_patch/cd2063604ea6a8c2683b4eb9b5f4c4da74592d87.patch -s True

echo "TEST next data dataset(TP)"
python3 ../src/main.py -p ../next_data_patch/bd8621ca1510e6e802df9855bdc35a04a3cfa932.patch -s True

echo "TEST next data dataset(FP)"
python3 ../src/main.py -p ../next_data_patch/2ba48b20049b5a76f34a85f853c9496d1b10533a.patch -s True
python3 ../src/main.py -p ../next_data_patch/599d41fb8ea8bd2a99ca9525dd69405020e43dda.patch -s True
python3 ../src/main.py -p ../next_data_patch/724b6bab0d75f1dc01fdfbf7fe8d4217a5cb90ba.patch -s True
python3 ../src/main.py -p ../next_data_patch/89d42b8c85b4c67d310c5ccaf491acbf71a260c3.patch -s True
python3 ../src/main.py -p ../next_data_patch/b1ae65c082f74536ec292b15766f2846f0238373.patch -s True