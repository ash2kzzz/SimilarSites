#! /usr/bin/bash

echo "TEST ground truth dataset"
python3 ../src/main.py -p ../ground_truth_patch/7c11910783a1ea17e88777552ef146cace607b3c.patch -s True
python3 ../src/main.py -p ../ground_truth_patch/e9db4ef6bf4ca9894bb324c76e01b8f1a16b2650.patch -s True

echo "TEST next data dataset(TP)"
python3 ../src/main.py -p ../next_data_patch/a240bc5c43130c6aa50831d7caaa02a1d84e1bce.patch -s True

echo "TEST next data dataset(FP)"
python3 ../src/main.py -p ../next_data_patch/1857c19941c87eb36ad47f22a406be5dfe5eff9f.patch -s True
python3 ../src/main.py -p ../next_data_patch/2f4e429c846972c8405951a9ff7a82aceeca7461.patch -s True
python3 ../src/main.py -p ../next_data_patch/6a19da111057f69214b97c62fb0ac59023970850.patch -s True
python3 ../src/main.py -p ../next_data_patch/724b6bab0d75f1dc01fdfbf7fe8d4217a5cb90ba.patch -s True
python3 ../src/main.py -p ../next_data_patch/ab9ddc87a9055c4bebd6524d5d761d605d52e557.patch -s True
python3 ../src/main.py -p ../next_data_patch/f7abf14f0001a5a47539d9f60bbdca649e43536b.patch -s True
python3 ../src/main.py -p ../next_data_patch/fa09fa60385abbf99342494b280da8b4aebbc0e9.patch -s True