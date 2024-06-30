#!/usr/bin/env python
# %%
from typing import List, Optional, Dict
from dataclasses import dataclass
import random
import math
import time
import requests


def truncdiv(a, b):
    return math.trunc(a / b)


def truncmod(a, b):
    return a - b * truncdiv(a, b)


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



@dataclass
class Node:
    token: str
    children: Optional[List['Node']] = None
    substitutions: Optional[Dict[str, 'Node']] = None
    parent: Optional['Node'] = None

    def __post_init__(self):
        if self.children:
            for child in self.children:
                child.parent = self

    @property
    def indicator(self):
        return self.token[0]
    
    @property
    def body(self):
        return self.token[1:]
    
    def isint(self):
        if self.indicator == 'I':
            return True
        if self.token == 'U-':
            return self.children[0].isint()
        return False
    
    def isbool(self):
        if self.token in ('T', 'F'):
            return True
        if self.token == 'U!':
            return self.children[0].isbool()
        return False
    
    def isstr(self):
        return self.indicator == 'S'

    def asint(self):
        if self.indicator == 'I':
            return c2b94(self.body)
        if self.token == 'U-':
            return - self.children[0].asint()
        raise ValueError(f"Expected integer, got {self.token}")
    
    def asbool(self):
        if self.token == 'T':
            return True
        if self.token == 'F':
            return False
        if self.token == 'U!':
            return not self.children[0].asbool()
        raise ValueError(f"Expected boolean, got {self.token}")
    
    def asstr(self):
        if self.indicator == 'S':
            return self.body
        raise ValueError(f"Expected string, got {self.token}")
    
    @classmethod
    def fromint(cls, value):
        if value >= 0:
            return cls('I' + b942c(value))
        return cls('U-', [cls('I' + b942c(-value))])

    def supdate(self, nodes, new_var=None, replacement=None):
        for node in nodes:
            if node.substitutions:
                if self.substitutions is None:
                    self.substitutions = {}
                self.substitutions.update(node.substitutions)
        if new_var is not None:
            assert replacement is not None
            if self.substitutions is None:
                self.substitutions = {}
            self.substitutions[new_var] = replacement

    def dump(self):
        s = self.token
        if self.children:
            for child in self.children:
                s += f" {child.dump()}"
        if self.substitutions:
            s += " {"
            for key, value in self.substitutions.items():
                s += f" {key}=<{value.dump()}>,"
            s += "}"
        return s

    def lookup(self, v):
        if self.substitutions and v in self.substitutions:
            return self.substitutions[v]
        return self.parent.lookup(v) if self.parent else None

    def rename(self, a, b):
        assert isinstance(a, str) and a.startswith('v') and len(a) > 1, a
        assert isinstance(b, str) and b.startswith('v') and len(b) > 1, b
        assert a != b, f"{a} == {b}"
        if self.indicator == 'v' and self.token == a:
            self.token = b
        if self.indicator == 'L' and self.body == a[1:]:
            return  # Stop renaming at next lambda boundary which matches
        if self.children:
            for child in self.children:
                child.rename(a, b)
        if self.substitutions:
            for value in self.substitutions.values():
                value.rename(a, b)

    def replace(self, node):
        self.substitutions = node.substitutions
        self.children = node.children
        self.token = node.token
        return True  # returned for convenience with step logic
    
    def squeeze(self, rep, nodes):
        self.supdate(nodes)
        self.supdate([rep])
        return self.replace(rep)


def parse(tokens):
    """ Parse list of tokens into tree of nodes """
    assert isinstance(tokens, list), f"Expected list, got {type(tokens)}"
    assert len(tokens) > 0, f"Expected non-empty list, got {tokens}"
    token = tokens.pop(0)
    assert isinstance(token, str) and len(token), f"bad token {token}"
    indicator = token[0]
    if indicator in 'TFvIS':
        return Node(token)
    if indicator in 'UL':
        return Node(token, [parse(tokens)])
    if indicator in 'B':
        return Node(token, [parse(tokens), parse(tokens)])
    if indicator in '?':
        return Node(token, [parse(tokens), parse(tokens), parse(tokens)])
    raise ValueError(f"Unknown indicator {indicator}")


def step(node):
    """ Single step of evaluation, returns False done """
    # Children first
    if node.children:
        for child in node.children:
            if step(child):
                return True
    # Values not the root of a replacement pattern
    if node.indicator in 'TFISL':
        return False
    # Variable replacement
    if node.indicator in 'v':
        value = node.lookup(node.token)
        if value is not None:
            return node.replace(value)
        return False
    # Unary
    if node.indicator == 'U':
        child, = node.children
        # String to integer
        if node.token == 'U#' and child.indicator == 'S':
            return node.replace(Node('I' + child.body))
        # Integer to string
        if node.token == 'U$' and child.indicator == 'I':
            return node.replace(Node('S' + child.body))
        return False
    # Binary
    if node.indicator == 'B':
        left, right = node.children
        # Application
        if node.body in '$':
            expression, = left.children
            old_var = 'v' + left.body
            new_var = 'v' + str(random.randint(1_000_000_000, 9_999_999_999))
            expression.rename(old_var, new_var)
            expression.supdate([left, node], new_var, right)
            return node.replace(expression)
        # Arithmetic
        if node.body in '+-*/%':
            a, b = left.asint(), right.asint()
            if node.token == 'B+':
                result = a + b
            elif node.token == 'B-':
                result = a - b
            elif node.token == 'B/':
                result = truncdiv(a, b)
            elif node.token == 'B%':
                result = truncmod(a, b)
            elif node.token == 'B*':
                result = a * b
            else:
                raise NotImplementedError(node.token)
            return node.replace(Node.fromint(result))
        # Boolean
        if node.body in '&|':
            a, b = left.asbool(), right.asbool()
            if node.token == 'B&':
                result = a and b
            elif node.token == 'B|':
                result = a or b
            else:
                raise NotImplementedError(node.token)
            return node.replace(Node('T' if result else 'F'))
        # Comparison
        if node.body in '<>=':
            # Equality
            if node.body in '=':
                # Boolean
                if left.isbool() and right.isbool():
                    result = left.asbool() == right.asbool()
                # Integer
                elif left.isint() and right.isint():
                    result = left.asint() == right.asint()
                # String
                elif left.isstr() and right.isstr():
                    result = left.asstr() == right.asstr()
                else:
                    return False
                return node.replace(Node('T' if result else 'F'))
            # Inequality
            elif node.body in '<>':
                if left.isint() and right.isint():
                    a, b = left.asint(), right.asint()
                    if node.body == '<':
                        result = a < b
                    elif node.body == '>':
                        result = a > b
                    else:
                        raise NotImplementedError(node.token)
                    return node.replace(Node('T' if result else 'F'))
                return False
            raise NotImplementedError(node.token)
        # String concatenation
        if node.body in '.':
            if left.isstr() and right.isstr():
                return node.replace(Node('S' + left.body + right.body))
            return False
        # String slicing
        if node.body in 'TD':
            if left.isint() and right.isstr():
                x = left.asint()
                y = right.asstr()
                result = y[:x] if node.body == 'T' else y[x:]
                return node.replace(Node('S' + result))
        raise NotImplementedError(node.token)
    # Conditional
    if node.indicator == '?':
        condition, true_value, false_value = node.children
        if condition.isbool():
            return node.replace(true_value if condition.asbool() else false_value)
        return False
    raise NotImplementedError(f"step {node.token}")


def evaluate(node):
    while step(node):
        pass
    return node


s = open('language_test.txt').read()

tokens = s.strip().split()
tree = parse(tokens)
tree = evaluate(tree)

if tree.indicator == 'S':
    print(decode(tree.body))


# %%

post_addr = "https://boundvariable.space/communicate"
# Authorization header
auth_path = '../../misc/SUBMISSION_HEADER.txt'
with open(auth_path, 'r') as file:
    auth = file.read()
assert auth.startswith("Authorization: Bearer ")
# convert to dict for requests
auth = {"Authorization": auth.lstrip("Authorization: ").strip()}

def post(s, filename=None):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert not s.startswith("S"), "Send bare string not encoded"
    data = 'S' + encode(s)
    response = requests.post(post_addr, headers=auth, data=data)
    response.raise_for_status()
    decoded = decode(response.text[1:].strip())
    if filename:
        with open(filename, 'w') as file:
            file.write(decoded)
    return decoded

result = post('get index', '../index/index.txt')
print(result)

# %% lambdaman
post('get lambdaman', '../lambdaman/info.txt')
for i in range(1, 22):
    time.sleep(4)
    print(f"Getting lambdaman {i}")
    post(f'get lambdaman{i}', f'../lambdaman/level{i}.txt')

# %% spaceship
post('get spaceship', '../spaceship/info.txt')
for i in range(1, 26):
    time.sleep(4)
    print(f"Getting spaceship {i}")
    post(f'get spaceship{i}', f'../spaceship/level{i}.txt')

# %% 3d
post('get 3d', '../3d/info.txt')
for i in range(1, 13):
    time.sleep(4)
    print(f"Getting 3d {i}")
    post(f'get 3d{i}', f'../3d/level{i}.txt')

# %% efficiency
post('get efficiency', '../efficiency/info.txt')
for i in range(1, 14):
    time.sleep(4)
    print(f"Getting efficiency {i}")
    post(f'get efficiency{i}', f'../efficiency/level{i}.txt')