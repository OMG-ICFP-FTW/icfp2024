#!/usr/bin/env python
#%%
import os

str_reference = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
decode_map = {chr(k): v for (k, v) in zip(list(range(33,33 + len(str_reference))),str_reference)}
encode_map = {v: k for (k, v) in decode_map.items()}
decode_trans = str.maketrans(decode_map)
encode_trans = str.maketrans(encode_map)


def decode(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    return s.translate(decode_trans)

def encode(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    return s.translate(encode_trans)


for i in range(25):
    path = f'level{i}.icfp'
    if os.path.exists(path):
        with open(path, 'r') as file:
            level = file.read().strip()
        if level.startswith('S') and len(level.split()) == 1:
            with open(f'level{i}.txt', 'w') as file:
                file.write(decode(level))