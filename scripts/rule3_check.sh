#! /usr/bin/bash

echo "TEST ground truth dataset"
python3 ../src/main.py -p ../ground_truth_patch/cc00bcaa589914096edef7fb87ca5cee4a166b5c.patch -s True
python3 ../src/main.py -p ../ground_truth_patch/e37542ba111f3974dc622ae0a21c1787318de500.patch -s True

echo "TEST next data dataset(TP)"
python3 ../src/main.py -p ../next_data_patch/1b1b43ee7a208096ecd79e626f2fc90d4a321111.patch -s True
python3 ../src/main.py -p ../next_data_patch/4b397c06cb987935b1b097336532aa6b4210e091.patch -s True
python3 ../src/main.py -p ../next_data_patch/5b825727d0871b23e8867f6371183e61628b4a26.patch -s True
python3 ../src/main.py -p ../next_data_patch/6b9831bfd9322b297eb6d44257808cc055fdc586.patch -s True
python3 ../src/main.py -p ../next_data_patch/7255355a0636b4eff08d5e8139c77d98f151c4fc.patch -s True
python3 ../src/main.py -p ../next_data_patch/a939d14919b799e6fff8a9c80296ca229ba2f8a4.patch -s True
python3 ../src/main.py -p ../next_data_patch/e14cadfd80d76f01bfaa1a8d745b1db19b57d6be.patch -s True
python3 ../src/main.py -p ../next_data_patch/e1d09c2c2f5793474556b60f83900e088d0d366d.patch -s True

echo "TEST next data dataset(FP)"
python3 ../src/main.py -p ../next_data_patch/12d4eb20d9d86fae5f84117ff047e966e470f7b9.patch -s True
python3 ../src/main.py -p ../next_data_patch/1596dae2f17ec5c6e8c8f0e3fec78c5ae55c1e0b.patch -s True
python3 ../src/main.py -p ../next_data_patch/44df42e66139b5fac8db49ee354be279210f9816.patch -s True
python3 ../src/main.py -p ../next_data_patch/4d3d2694e168c542b088eef5059d31498f679020.patch -s True
python3 ../src/main.py -p ../next_data_patch/5ce76fe1eead179c058d9151ee1f4088cfdc1c6b.patch -s True
python3 ../src/main.py -p ../next_data_patch/62d101d5f422cde39b269f7eb4cbbe2f1e26f9d4.patch -s True
python3 ../src/main.py -p ../next_data_patch/691c041bf20899fc13c793f92ba61ab660fa3a30.patch -s True
python3 ../src/main.py -p ../next_data_patch/7abcb0b10668eaf3c174ff383f3b2a7a8c95fb34.patch -s True
python3 ../src/main.py -p ../next_data_patch/aa8c85affe3facd3842c8912186623415931cc72.patch -s True
python3 ../src/main.py -p ../next_data_patch/bdb7fdb0aca8b96cef9995d3a57e251c2289322f.patch -s True
python3 ../src/main.py -p ../next_data_patch/ca0aa17f2db3468fd017038d23a78e17388e2f67.patch -s True
python3 ../src/main.py -p ../next_data_patch/d636fc5dd692c8f4e00ae6e0359c0eceeb5d9bdb.patch -s True