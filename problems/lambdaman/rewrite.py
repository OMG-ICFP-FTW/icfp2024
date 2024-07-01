#!/usr/bin/env python
#%%
from collections import defaultdict
from typing import List, Tuple, Union, Any, Optional, Dict
from dataclasses import dataclass, field


def toint(s: str) -> int:
    value = 0
    for c in s:
        value *= 94
        value += ord(c) - 33
    return value


strmap = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"

def decode(s):
    return ''.join(strmap[ord(c) - 33] for c in s)


assert toint('!') == 0
assert toint('"') == 1
assert toint('"!') == 94
assert decode('B%,,/}Q/2,$_') == 'Hello World!'


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
    'U#': 'convert-str-to-int',  # defined in the template
    'U$': 'convert-int-to-str',  # defined in the template
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
    'BT': 'take',  # defined in the template
    'BD': 'drop',  # defined in the template
    'B$': '',  # Bit of a hack since the first arg will be a function
}


def unparse(node) -> str:
    """ Unparse a node to a string in scheme """
    if node.indicator == 'T':
        return '#t'
    if node.indicator == 'F':
        return '#f'
    if node.indicator == 'I':
        return str(toint(node.body))
    if node.indicator == 'S':
        return '"' + decode(node.body) + '"'
    if node.indicator == 'v':
        return f"v{toint(node.body)}"
    if node.indicator in 'UL':
        child, = node.children
        c = unparse(child)
        if node.indicator == 'L':
            v = f"v{toint(node.body)}"
            return f"(lambda ({v}) {c})"
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


TEMPLATE = """
(define (convert-str-to-int str)
  (foldl
    (lambda (value char)
        (+ (* value 94) (- (char->integer char) 33)))
    0 (string->list str)))

(define (convert-int-to-str num)
  (define (build-string n acc)
    (if (zero? n)
        (list->string acc)
        (let ((quotient (quotient n 94))
              (remainder (remainder n 94)))
          (build-string quotient 
                        (cons (integer->char (+ remainder 33)) acc)))))
  (if (zero? num)
      "!" ; Special case for 0, which corresponds to '!'
      (build-string num '())))

(define take (lambda (x y) (substring x 0 (- (string-length x) y))))
(define drop (lambda (x y) (substring x y (string-length x))))

(display
{scm}
)
"""

def main(s):
    node = parse(s)
    scm = unparse(node)
    return TEMPLATE.format(scm=scm)

main(open('language_test.txt').read())

# %%

if __name__ == '__main__':
    import sys
    print(main(sys.stdin.read()))