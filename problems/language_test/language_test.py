#!/usr/bin/env python
# %%
import os
import requests

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

path = 'language_test.txt'
if not os.path.exists(path):
    data = encode('get language_test')
    response = requests.post(post_addr, headers=auth, data=data)
    response.raise_for_status()
    language_test = response.text.strip()
    with open(path, 'w') as file:
        file.write(language_test)
with open(path, 'r') as file:
    language_test = file.read()
print(language_test)


# %%


test_str = r'''B= B$ B$ B$ B$ L$ L$ L$ L# v$ I" I# I$ I% I$ ? B= B$ L$ v$ I+ I+ ? B= BD I$ S4%34 S4 ? B= BT I$ S4%34 S4%3 ? B= B. S4% S34 S4%34 ? U! B& T F ? B& T T ? U! B| F F ? B| F T ? B< U- I$ U- I# ? B> I$ I# ? B= U- I" B% U- I$ I# ? B= I" B% I( I$ ? B= U- I" B/ U- I$ I# ? B= I# B/ I( I$ ? B= I' B* I# I$ ? B= I$ B+ I" I# ? B= U$ I4%34 S4%34 ? B= U# S4%34 I4%34 ? U! F ? B= U- I$ B- I# I& ? B= I$ B- I& I# ? B= S4%34 S4%34 ? B= F F ? B= I$ I$ ? T B. B. SM%,&k#(%#+}IEj}3%.$}z3/,6%},!.'5!'%y4%34} U$ B+ I# B* I$> I1~s:U@ Sz}4/}#,!)-}0/).43}&/2})4 S)&})3}./4}#/22%#4 S").!29}q})3}./4}#/22%#4 S").!29}q})3}./4}#/22%#4 S").!29}q})3}./4}#/22%#4 S").!29}k})3}./4}#/22%#4 S5.!29}k})3}./4}#/22%#4 S5.!29}_})3}./4}#/22%#4 S5.!29}a})3}./4}#/22%#4 S5.!29}b})3}./4}#/22%#4 S").!29}i})3}./4}#/22%#4 S").!29}h})3}./4}#/22%#4 S").!29}m})3}./4}#/22%#4 S").!29}m})3}./4}#/22%#4 S").!29}c})3}./4}#/22%#4 S").!29}c})3}./4}#/22%#4 S").!29}r})3}./4}#/22%#4 S").!29}p})3}./4}#/22%#4 S").!29}{})3}./4}#/22%#4 S").!29}{})3}./4}#/22%#4 S").!29}d})3}./4}#/22%#4 S").!29}d})3}./4}#/22%#4 S").!29}l})3}./4}#/22%#4 S").!29}N})3}./4}#/22%#4 S").!29}>})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4 S!00,)#!4)/.})3}./4}#/22%#4'''

tokens = test_str.strip().split()

len(tokens)
