#!/usr/bin/env python
# %%
import requests
import time
import sys

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
decode_trans = str.maketrans(decode_map)


def request(s):
    data = 'S' + s.translate(encode_trans)
    response = requests.post(post_addr, headers=auth, data=data)
    response.raise_for_status()
    return response.text


if __name__ == '__main__':
    for i in sys.argv[1:]:
        print(f"level{i}")
        with open(f"solution{i}.txt") as f:
            solution = f.read()
        response = request(f"solve spaceship{i} {solution}")
        print(response[1:].translate(decode_trans))
        time.sleep(5)