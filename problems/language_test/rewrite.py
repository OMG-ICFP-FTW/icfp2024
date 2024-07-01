#!/usr/bin/env python
#%%
from collections import defaultdict
from typing import List, Tuple, Union, Any, Optional, Dict
from dataclasses import dataclass, field
import os
import sys


@dataclass
class Node:
    token: str
    children: List['Node'] = field(default_factory=list)

    @property
    def indicator(self):
        return self.token[0]
    
    @property
    def body(self):
        return self.token[1:]


def parse(prog) -> Node:
    tokens = prog.strip().split() if isinstance(prog, str) else prog
    node = Node(tokens.pop(0))
    if node.indicator in 'TFvISxyz':
        return node
    if node.indicator in 'LU':
        node.children = [parse(tokens)]
        return node
    if node.indicator in 'B':
        node.children = [parse(tokens), parse(tokens)]
        return node
    if node.indicator in '?':
        node.children = [parse(tokens), parse(tokens), parse(tokens)]
        return node
    raise ValueError(f"Unknown indicator {node.indicator}, {node.token}")


unary_funcs = {
    'U!': 'not',
    'U-': '-',
    'U#': 's2i',  # defined in header
    'U$': 'i2s',  # defined in header
}


binary_funcs = {
    'B&': 'and',
    'B|': 'or',
    'B+': '+',
    'B-': '-',
    'B*': '*',
    'B/': 'quotient',
    'B%': 'remainder',
    'B<': '<',
    'B>': '>',
    'B=': 'equal?',
    'B.': 'string-append',
    'BT': 'take',  # defined in header
    'BD': 'drop',  # defined in header
    'B$': '',  # Bit of a hack since the first arg will be a function
}


def varname(body):
    """ Convert variable tag to a v-prefixed hex name """
    return 'v' + ''.join(f"{ord(c):2x}" for c in body)


def escape(s):
    """ Return a string escaped for use by scheme """
    e = s.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n","\\n")
    return f"\"{e}\""


def unparse(node) -> str:
    """ Unparse a node to a string in scheme """
    if node.indicator == 'T':
        return '#t'
    if node.indicator == 'F':
        return '#f'
    if node.indicator == 'I':
        return f"(s2i {escape(node.body)})"
    if node.indicator == 'S':
        return escape(node.body)
    if node.indicator == 'v':
        return varname(node.body)
    if node.indicator in 'UL':
        c = unparse(node.children[0])
        if node.indicator == 'L':
            return f"(lambda ({varname(node.body)}) {c})"
        func = unary_funcs[node.token]
        return f"({func} {c})"
    if node.indicator in 'B':
        left, right = node.children
        a, b = unparse(left), unparse(right)
        func = binary_funcs[node.token]
        return f"({func} {a} {b})"
    if node.indicator == '?':
        cond, first, second = node.children
        c, f, s = unparse(cond), unparse(first), unparse(second)
        return f"(if {c} {f} {s})"
    raise NotImplementedError(f"Missing {node.token[:9]}")


def main(s):
    node = parse(s)
    scm = unparse(node)
    with open('rewrite.scm') as f:
        header = f.read()
    code = f"\n(render\n;BEGIN CODE\n{scm}\n;END CODE\n)"
    return header + code


# def main(s, path='/tmp/main.scm'):
#     src = trans(s)
#     with open(path, 'w') as f:
#         f.write(src)
#     prog = path + '.out'
#     os.system(f"csc {path} -o {prog}")
#     os.system(f"{prog}")
#     print('Done')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if not os.path.exists(filepath):
            print(";Defaulting to language_test")
            filepath = 'language_test.txt'
        with open(filepath) as f:
            icfp = f.read()
    else:
        print(";Reading from stdin")
        icfp = sys.stdin.read()
    print(main(icfp))