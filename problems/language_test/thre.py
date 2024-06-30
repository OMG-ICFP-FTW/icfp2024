#!/usr/bin/env python
# %%


r'''

ICFP language

An Interstellar Communication Functional Program (ICFP) consists of a list of space-separated tokens. A token consists of one or more printable ASCII characters, from ASCII code 33 ('!') up to and including code 126 ('~'). In other words, there are 94 possible characters, and a token is a nonempty sequence of such characters.

The first character of a token is called the indicator, and determines the type of the token. The (possibly empty) remainder of the token is called body. The different token types are explained in the next subsections.
Booleans

indicator = T and an empty body represents the constant true, and indicator = F and an empty body represents the constant false.
Integers

indicator = I, requires a non-empty body.

The body is interpreted as a base-94 number, e.g. the digits are the 94 printable ASCII characters with the exclamation mark representing 0, double quotes 1, etc. For example, I/6 represent the number 1337.
Strings

indicator = S

The Cult of the Bound variable seems to use a system similar to ASCII to encode characters, but ordered slightly differently. Specifically, ASCII codes 33 to 126 from the body can be translated to human readable text by converting them according to the following order:

abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;<=>?@[\]^_`|~<space><newline>

Here <space> denotes a single space character, and <newline> a single newline character. For example, SB%,,/}Q/2,$_ represents the string "Hello World!".
Unary operators

indicator = U, requires a body of exactly 1 character long, and should be followed by an ICFP which can be parsed from the tokens following it.
Character	Meaning	Example
-	Integer negation	U- I$ -> -3
!	Boolean not	U! T -> false
#	string-to-int: interpret a string as a base-94 number	U# S4%34 -> 15818151
$	int-to-string: inverse of the above	U$ I4%34 -> test

The -> symbol in this table should be read as "will evaluate to", see Evaluation.
Binary operators

indicator = B, requires a body of exactly 1 character long, and should be followed by two ICFPs (let's call them x and y).
Character	Meaning	Example
+	Integer addition	B+ I# I$ -> 5
-	Integer subtraction	B- I$ I# -> 1
*	Integer multiplication	B* I$ I# -> 6
/	Integer division (truncated towards zero)	B/ U- I( I# -> -3
%	Integer modulo	B% U- I( I# -> -1
<	Integer comparison	B< I$ I# -> false
>	Integer comparison	B> I$ I# -> true
=	Equality comparison, works for int, bool and string	B= I$ I# -> false
|	Boolean or	B| T F -> true
&	Boolean and	B& T F -> false
.	String concatenation	B. S4% S34 -> "test"
T	Take first x chars of string y	BT I$ S4%34 -> "tes"
D	Drop first x chars of string y	BD I$ S4%34 -> "t"
$	Apply term x to y (see Lambda abstractions)	
If

indicator = ? with an empty body, followed by three ICFPs: the first should evaluate to a boolean, if it's true then the second is evaluated for the result, else the third. For example:

? B> I# I$ S9%3 S./

evaluates to no.
Lambda abstractions

indicator = L is a lambda abstraction, where the body should be interpreted as a base-94 number in the same way as integers, which is the variable number, and it takes one ICFP as argument. indicator = v is a variable, with again a body being the base-94 variable number.

When the first argument of the binary application operator $ evaluates to a lambda abstraction, the second argument of the application is assigned to that variable. For example, the ICFP

B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK

represents the program (e.g. in Haskell-style)

((\v2 -> \v3 -> v2) ("Hello" . " World!")) 42

which would evaluate to the string "Hello World!".
Evaluation

The most prevalent ICFP messaging software, Macroware Insight, evaluates ICFP messages using a call-by-name strategy. This means that the binary application operator is non-strict; the second argument is substituted in the place of the binding variable (using capture-avoiding substitution). If an argument is not used in the body of the lambda abstraction, such as v3 in the above example, it is never evaluated. When a variable is used several times, the expression is evaluated multiple times.

For example, evaluation would take the following steps:

B$ L# B$ L" B+ v" v" B* I$ I# v8
B$ L" B+ v" v" B* I$ I#
B+ B* I$ I# B* I$ I#
B+ I' B* I$ I#
B+ I' I'
I-

Limits

As communication with Earth is complicated, the Cult seems to have put some restrictions on their Macroware Insight software. Specifically, message processing is aborted when exceeding 10_000_000 beta reductions. Built-in operators are strict (except for B$, of course) and do not count towards the limit of beta reductions. Contestants' messages therefore must stay within these limits.

For example, the following term, which evaluates to 16, uses 109 beta reductions during evaluation:

B$ B$ L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v# L" L# ? B= v# I! I" B$ L$ B+ B$ v" v$ B$ v" v$ B- v# I" I%

Researchers expect that the limit on the amount beta reductions is the only limit that contestants may run into, but there seem to also be some (unknown) limits on memory usage and total runtime.
Unknown operators

The above set of language constructs are all that researchers have discovered, and it is conjectured that the Cult will never use anything else in their communication towards Earth. However, it is unknown whether more language constructs exist.
'''


from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass, field
import random

import math

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
    
    def asint(self):
        if self.indicator == 'I':
            return c2b94(self.body)
        if self.token == 'U-':
            return - self.children[0].asint()
        raise ValueError(f"Expected integer, got {self.token}")
    
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
    # Values not the root of a replacement pattern
    if node.indicator in 'TFISL':
        return False
    # Variable replacement
    if node.indicator in 'v':
        value = node.lookup(node.token)
        if value is not None:
            node.token = value.token
            node.children = value.children
            node.substitutions = value.substitutions
            return True
        return False
    # Unary
    if node.indicator == 'U':
        if step(node.children[0]):
            return True
        child = node.children[0]
        # Negation
        if node.body in '-':
            # Cancel out
            if child.token == 'U-':
                inner = child.children[0]
                node.supdate([inner, child])
                node.children = inner.children
                node.token = inner
                return True
            return False
        # Not
        if node.body in '!':
            if child.token in ('T', 'F'):
                result = 'F' if child.token == 'T' else 'T'
                node.substitutions = None
                node.children = None
                node.token = result
                return True
            return False
        raise ValueError(f"{node.token}")
    # Binary
    if node.indicator == 'B':
        # Application
        if node.body in '$':
            if step(node.children[0]):
                return True
            lambda_ = node.children[0]
            expression = lambda_.children[0]
            replacement = node.children[1]
            old_var = 'v' + lambda_.body
            new_var = 'v' + str(random.randint(1_000_000_000, 9_999_999_999))
            expression.rename(old_var, new_var)
            node.supdate([lambda_, expression], new_var, replacement)
            node.children = expression.children
            node.token = expression.token
            return True
        # Arithmetic
        if node.body in '+-*/%':
            if step(node.children[0]):
                return True
            if step(node.children[1]):
                return True
            a = node.children[0].asint()
            b = node.children[1].asint()
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
            node.replace(Node.fromint(result))
            return True
        # Boolean
        if node.body in '&|':
            # First try the left side
            if step(node.children[0]):
                return True
            if step(node.children[1]):
                return True
            left = node.children[0]
            right = node.children[1]
            if node.body == '&':
                if left.token == 'F' or right.token == 'F':
                    result = Node('F')
                elif left.token == 'T':
                    result = right
                elif right.token == 'T':
                    result = left
                else:
                    return False
            elif node.body == '|':
                if left.token == 'T' or right.token == 'T':
                    result = Node('T')
                elif left.token == 'F':
                    result = right
                elif right.token == 'F':
                    result = left
                else:
                    return False
            else:
                raise ValueError(f"{node.token}")
            node.supdate([result])
            node.children = result.children
            node.token = result.token
            return True
        # Comparison
        if node.body in '<>=':
            if step(node.children[0]):
                return True
            if step(node.children[1]):
                return True
            left = node.children[0]
            right = node.children[1]
            # Equality
            if node.body in '=':
                # Boolean
                if left.token in ('T', 'F'):
                    assert right.token in ('T', 'F'), right.token
                    result = left.token == right.token
                # Variable
                elif left.indicator == 'v' or right.indicator == 'v':
                    if left.token == right.token:
                        result = True
                    return False  # Not enough information
                # Integer, String
                elif left.indicator in 'IS':
                    assert left.indicator == right.indicator, f"{left.token} {right.token}"
                    result = left.token == right.token
                # Negative numbers
                elif left.token == 'U-' and right.token == 'U-':
                    lefter = left.children[0]
                    lefter.supdate([left])
                    righter = right.children[0]
                    righter.supdate([right])
                    node.children = [lefter, righter]
                    return True
                else:
                    raise ValueError(f"Unknown comparison {left.token} {right.token}")
            elif node.body in '<>':
                if left.indicator == 'I':
                    x = c2b94(left.body)
                elif left.token == 'U-':
                    assert left.children[0].indicator == 'I', left
                    x = - c2b94(left.children[0].body)
                if right.indicator == 'I':
                    y = c2b94(right.body)
                elif right.token == 'U-':
                    y = - c2b94(right.children[0].body)
                result = (x < y) if (node.body == '<') else (x > y)
            else:
                raise ValueError(f"{node.token}")
            node.substitutions = None
            node.children = None
            node.token = 'T' if result else 'F'
            return True
        # String concatenation
        if node.body in '.':
            if step(node.children[0]):
                return True
            if step(node.children[1]):
                return True
            left = node.children[0]
            right = node.children[1]
            assert left.indicator == 'S', left
            assert right.indicator == 'S', right
            result = left.body + right.body
            node.substitutions = None
            node.children = None
            node.token = 'S' + result
            return True
        # String slicing
        if node.body in 'TD':
            if step(node.children[0]):
                return True
            if step(node.children[1]):
                return True
            left = node.children[0]
            right = node.children[1]
            assert left.indicator == 'I', left
            assert right.indicator == 'S', right
            x = c2b94(left.body)
            y = right.body
            result = y[:x] if node.body == 'T' else y[x:]
            node.substitutions = None
            node.children = None
            node.token = 'S' + result
            return True
        raise NotImplementedError(node.token)
    # Conditional
    if node.indicator == '?':
        if step(node.children[0]):
            return True
        condition = node.children[0]
        assert condition.token in ('T', 'F'), condition.token
        if condition.token == 'T':
            value = node.children[1]
        else:
            value = node.children[2]
        node.supdate([value])
        node.children = value.children
        node.token = value.token
        return True
    raise NotImplementedError(f"step {node.token}")


s = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
# s = 'B$ B$ L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v# L" L# ? B= v# I! I" B$ L$ B+ B$ v" v$ B$ v" v$ B- v# I" I%'
s = open('language_test.txt').read()

tokens = s.strip().split()
tree = parse(tokens)



for i in range(1000):
    print(tree.dump())
    if not step(tree):
        print("Done at step", i)
        break



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

if tree.indicator == 'S':
    print(decode(tree.body))


# %%
