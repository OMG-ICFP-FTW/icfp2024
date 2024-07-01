#!/usr/bin/env python
# %%



strmap = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"

def decode(s):
    return ''.join(strmap[ord(c) - 33] for c in s)

def encode(s):
    return ''.join(chr(strmap.index(c) + 33) for c in s)

with open('solution23.txt') as f:
    solution = f.read()
with open('solution23.icfp', 'w') as f:
    f.write('S' + encode(solution))

'''
Example uploading with curl:

curl -X POST 

'''

# %%
# stolen from lambdaman6
RLE = 'B$ B$ L" B$ L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v# L$ L# ? B= v# I" v" B. v" B$ v$ B- v# I" Sl I#,'

def toint(s):
    value = 0
    for c in s:
        value *= 94
        value += ord(c) - 33
    return value


def fromint(value):
    s = ''
    while value:
        s = chr(value % 94 + 33) + s
        value //= 94
    return s


filename = 'solution23.txt'
with open(filename) as f:
    solution = f.read()

current_char = solution[0]
current_run = 1
chunks = []
for i in range(1, len(solution)):
    if solution[i] == current_char:
        current_run += 1
    else:
        if current_run > 1000:
            chunks.append((i - current_run, i))
        current_char = solution[i]
        current_run = 1

chunks