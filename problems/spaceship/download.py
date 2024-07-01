#!/usr/bin/env python
# %%
import requests
import os
import json
import time
from dataclasses import dataclass, field


post_addr = "https://boundvariable.space/communicate"
# Authorization header
auth_path = '../../misc/SUBMISSION_HEADER.txt'
with open(auth_path, 'r') as file:
    auth = file.read()
assert auth.startswith("Authorization: Bearer ")
# convert to dict for requests
auth = {"Authorization": auth.lstrip("Authorization: ").strip()}

str_reference = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
decode_map = {chr(k): v for (k, v) in zip(list(range(33,33 + len(str_reference))),str_reference)}
encode_map = {v: k for (k, v) in decode_map.items()}
encode_trans = str.maketrans(encode_map)


def request(s):
    data = 'S' + s.translate(encode_trans)
    response = requests.post(post_addr, headers=auth, data=data)
    response.raise_for_status()
    return response.text


for i in range(1, 26):
    print(f"level{i}")
    with open(f"level{i}.icfp", 'w') as f:
        f.write(request(f"get spaceship{i}"))
    time.sleep(5)