#!/usr/bin/env python
# %% imports
import requests
import os
import json
import hashlib
import time
import random
from dataclasses import dataclass, field

# %% file paths and constants

post_addr = "https://boundvariable.space/communicate"
# Authorization header
auth_path = '../misc/SUBMISSION_HEADER.txt'
with open(auth_path, 'r') as file:
    auth = file.read()
assert auth.startswith("Authorization: Bearer ")
# convert to dict for requests
auth = {"Authorization": auth.lstrip("Authorization: ").strip()}

# Cache for requests and responses, as simple json files
cache_path = '../cache/'
os.makedirs(cache_path, exist_ok=True)

# %% decode and encode

str_reference = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
decode_map = {chr(k): v for (k, v) in zip(list(range(33,33 + len(str_reference))),str_reference)}
encode_map = {v: k for (k, v) in decode_map.items()}
decode_trans = str.maketrans(decode_map)
encode_trans = str.maketrans(encode_map)

def decode(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert s.startswith("S"), f"Expected string, got {s}"
    return s[1:].translate(decode_trans)

def encode(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    return "S" + s.translate(encode_trans)


assert encode("Hello World!") == "SB%,,/}Q/2,$_", encode("Hello World!")
assert decode("SB%,,/}Q/2,$_") == "Hello World!", decode("SB%,,/}Q/2,$_")

# %% cache requests with the server

def request(s, force=False):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert not s.startswith("S"), "Send bare string not encoded"
    data = encode(s)
    filename = hashlib.sha256(data.encode()).hexdigest()
    filepath = os.path.join(cache_path, filename)
    if force or not os.path.exists(filepath) and not force:
        time.sleep(5)
        response = requests.post(post_addr, headers=auth, data=data)
        response.raise_for_status()
        decoded = decode(response.text)
        with open(filepath, 'w') as file:
            json.dump({"request": s, "encoded":data, "response": response.text, "decoded": decoded}, file)
    with open(filepath, 'r') as file:
        return json.load(file)

# # %% Get index
# result = request('get index', force=True)
# with open('../problems/index/index.txt', 'w') as file:
#     file.write(result['decoded'])

# # %%  Get lambdaman info and send solutions
# lm_cache_path = '../problems/lambdaman/'
# os.makedirs(lm_cache_path, exist_ok=True)
# result = request('get lambdaman', force=True)
# with open(os.path.join(lm_cache_path, 'info.txt'), 'w') as file:
#     file.write(result['decoded'])
# for i in range(1, 6):
#     path = f'../problems/lambdaman/solution{i}.txt'
#     if os.path.exists(path):
#         with open(path, 'r') as file:
#             solution = file.read().strip()
#     msg = f"solve lambdaman{i} {solution}"
#     result = request(msg)
#     print(result['decoded'])

# # %% Get spaceship info
# ss_cache_path = '../problems/spaceship/'
# os.makedirs(ss_cache_path, exist_ok=True)
# result = request('get spaceship', force=True)
# with open(os.path.join(ss_cache_path, 'info.txt'), 'w') as file:
#     file.write(result['decoded'])
# # %% Download spaceship levels
# for i in range(1, 22):
#     path = f'../problems/spaceship/level{i}.txt'
#     if not os.path.exists(path):
#         msg = f"get spaceship{i}"
#         result = request(msg)
#         with open(path, 'w') as file:
#             file.write(result['decoded'])
# # %% Upload spaceship solutions
# for i in range(1, 22):
#     path = f'../problems/spaceship/solution{i}.txt'
#     if os.path.exists(path):
#         with open(path, 'r') as file:
#             solution = file.read().strip()
#         msg = f"solve spaceship{i} {solution}"
#         result = request(msg)
#         print(result['decoded'])

# %% get 3d info
result = request('get 3d', force=True)
with open('../problems/3d/info.txt', 'w') as file:
    file.write(result['decoded'])
# %% get 3d levels
for i in range(1, 13):
    path = f"../problems/3d/level{i}.txt"
    if not os.path.exists(path):
        msg = f"get 3d{i}"
        result = request(msg)
        with open(path, 'w') as file:
            file.write(result['decoded'])

# # %% echo
# done = False
# while not done:
#     result = request(f'echo {hash(random.randbytes(1024))}', force=True)
#     print(result['decoded'])
#     if "You scored some points" not in result['decoded']:
#         done = True
#     time.sleep(5)
