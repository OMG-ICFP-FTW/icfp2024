#!/usr/bin/env python
# %% translate icfp language to scheme
import sys
import subprocess
import tempfile
import os

def c2b94(s):
    value = 0
    for c in s:
        value *= 94
        value += ord(c) - 33
    return value


def b942c(value):
    assert isinstance(value, int) and value >= 0, value
    if value == 0:
        return '!'
    s = ""
    while value:
        value, r = divmod(value, 94)
        s = chr(r + 33) + s
    return s


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


class Node:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children or []

def tokenize(icfp_code):
    return icfp_code.split()

def parse(tokens):
    def parse_expression(index):
        if index >= len(tokens):
            return None, index
        
        token = tokens[index]
        if token[0] in 'TF':
            return Node('bool', token), index + 1
        elif token[0] == 'I':
            return Node('int', token[1:]), index + 1
        elif token[0] == 'S':
            return Node('string', decode(token[1:])), index + 1
        elif token[0] == 'U':
            node, next_index = parse_expression(index + 1)
            return Node('unary', token[1], [node]), next_index
        elif token[0] == 'B':
            left, next_index = parse_expression(index + 1)
            right, next_index = parse_expression(next_index)
            return Node('binary', token[1], [left, right]), next_index
        elif token[0] == '?':
            cond, next_index = parse_expression(index + 1)
            true_branch, next_index = parse_expression(next_index)
            false_branch, next_index = parse_expression(next_index)
            return Node('if', None, [cond, true_branch, false_branch]), next_index
        elif token[0] == 'L':
            body, next_index = parse_expression(index + 1)
            return Node('lambda', token[1:], [body]), next_index
        elif token[0] == 'v':
            return Node('var', token[1:]), index + 1
        else:
            return Node('unknown', token), index + 1

    root, _ = parse_expression(0)
    return root

def emit_scheme(node):
    if node.type == 'bool':
        return '#t' if node.value == 'T' else '#f'
    elif node.type == 'int':
        return str(c2b94(node.value))
    elif node.type == 'string':
        # Simplified string conversion
        return f'"{node.value}"'
    elif node.type == 'unary':
        op = {'-': '-', '!': 'not', '#': 'string->number', '$': 'number->string'}[node.value]
        return f'({op} {emit_scheme(node.children[0])})'
    elif node.type == 'binary':
        if node.value == '$':
            # Special handling for application
            func = emit_scheme(node.children[0])
            arg = emit_scheme(node.children[1])
            return f'({func} {arg})'
        op = {'+': '+', '-': '-', '*': '*', '/': 'quotient', '%': 'remainder',
              '<': '<', '>': '>', '=': '=', '|': 'or', '&': 'and', '.': 'string-append'}[node.value]
        return f'({op} {emit_scheme(node.children[0])} {emit_scheme(node.children[1])})'
    elif node.type == 'if':
        return f'(if {emit_scheme(node.children[0])} {emit_scheme(node.children[1])} {emit_scheme(node.children[2])})'
    elif node.type == 'lambda':
        var_num = c2b94(node.value)
        return f'(lambda (v{var_num}) {emit_scheme(node.children[0])})'
    elif node.type == 'var':
        var_num = c2b94(node.value)
        return f'v{var_num}'
    else:
        return node.value  # Unknown node type

def icfp_to_scheme(icfp_code):
    tokens = tokenize(icfp_code)
    parse_tree = parse(tokens)
    return "(display " + emit_scheme(parse_tree) + ")"


def main(i):
    input_file = f"efficiency{i}.icfp"
    scheme_file = f"efficiency{i}.scm"
    with open(input_file, 'r') as f:
        icfp_code = f.read().strip()
    scheme_code = icfp_to_scheme(icfp_code)
    with open(scheme_file, 'w') as f:
        f.write(scheme_code)
    output_file = f"efficiency{i}.out"
    os.system(f"csc {scheme_file} -o {output_file}")
    print("Generated", output_file)
    # for opt in range(1, 6):
    #     output_file = f"efficiency{i}.O{opt}"
    #     os.system(f"csc {scheme_file} -O{opt} -o {output_file}")

if __name__ == '__main__':
    for i in range(1, 14):
        main(i)