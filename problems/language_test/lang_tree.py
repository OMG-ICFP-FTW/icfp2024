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

@dataclass
class Node:
    token: str
    children: Optional[List['Node']] = None
    parent: Optional['Node'] = None
    substitutions: Dict[str, 'Node'] = field(default_factory=dict)

    @property
    def indicator(self):
        return self.token[0]
    
    @property
    def body(self):
        return self.token[1:]
    
    def lookup(self, v):
        if v in self.substitutions:
            return self.substitutions[v]
        return self.parent.lookup(v) if self.parent else None

    def dump(self):
        s = self.token
        if self.children:
            for child in self.children:
                s += " " + child.dump()
        if self.substitutions:
            s += " {"
            for k, v in self.substitutions.items():
                s += f" {k}: <>,"
            s += "}"
        return s
    
    def rename(self, a, b):
        assert isinstance(a, str) and a.startswith('v') and len(a) > 1, a
        assert isinstance(b, str) and b.startswith('v') and len(b) > 1, b
        assert a != b, f"{a} == {b}"
        if self.token == a:
            self.token = b
        for child in self.children or []:
            child.rename(a, b)


@dataclass
class Boolean(Node):
    def check(self):
        assert self.indicator in ('T', 'F'), self
        assert not len(self.body), self
        assert self.children is None, self


@dataclass
class Variable(Node):
    def check(self):
        assert self.indicator == "v", self
        assert len(self.body), self
        assert self.children is None, self


@dataclass
class Integer(Node):
    def check(self):
        assert self.indicator == "I", self
        assert len(self.body), self
        assert self.children is None, self


@dataclass
class String(Node):
    def check(self):
        assert self.indicator == "S", self
        assert len(self.body), self
        assert self.children is None, self


@dataclass
class Unary(Node):
    @property
    def op(self):
        return self.body
    
    @property
    def expr(self):
        return self.children[0]

    def check(self):
        assert self.indicator == "U", self
        assert len(self.body) == 1, self
        assert len(self.children) == 1, self
        assert all(c.parent == self for c in self.children), self
        self.expr.check()


@dataclass
class Lambda(Node):
    @property
    def var(self):
        return 'v' + self.body

    @property
    def expr(self):
        return self.children[0]

    def check(self):
        assert self.indicator == "L", self
        assert len(self.body), self
        assert len(self.children) == 1, self
        assert all(c.parent == self for c in self.children), self
        self.expr.check()


@dataclass
class Binary(Node):
    @property
    def op(self):
        return self.body
    
    @property
    def left(self):
        return self.children[0]
    
    @property
    def right(self):
        return self.children[1]

    def check(self):
        assert self.indicator == "B", self
        assert len(self.body) == 1, self
        assert self.op in "+-*/%<>=|&.TD$", self
        assert len(self.children) == 2, self
        assert all(c.parent == self for c in self.children), self
        self.left.check()
        self.right.check()


@dataclass
class Conditional(Node):
    @property
    def condition(self):
        return self.children[0]
    
    @property
    def then(self):
        return self.children[1]
    
    @property
    def otherwise(self):
        return self.children[2]

    def check(self):
        assert self.token == "?", self
        assert len(self.children) == 3, self
        assert all(c.parent == self for c in self.children), self
        self.condition.check()
        self.then.check()
        self.otherwise.check()


def parse(tokens, parent):
    """ Parse list of tokens into tree of nodes """
    assert isinstance(tokens, list), f"Expected list, got {type(tokens)}"
    assert len(tokens) > 0, f"Expected non-empty list, got {tokens}"
    token = tokens.pop(0)
    assert isinstance(token, str) and len(token), f"bad token {token}"
    indicator = token[0]
    if indicator in ('T', 'F'):
        return Boolean(token, parent=parent)
    if indicator == "v":
        return Variable(token, parent=parent)
    if indicator == "I":
        return Integer(token, parent=parent)
    if indicator == "S":
        return String(token, parent=parent)
    if indicator == "U":
        node = Unary(token, parent=parent)
        expr = parse(tokens, node)
        node.children = [expr]
        return node
    if indicator == "L":
        node = Lambda(token, parent=parent)
        body = parse(tokens, node)
        node.children = [body]
        return node
    if indicator == "B":
        node = Binary(token, parent=parent)
        left = parse(tokens, node)
        right = parse(tokens, node)
        node.children = [left, right]
        return node
    if indicator == "?":
        node = Conditional(token, parent=parent)
        condition = parse(tokens, node)
        then = parse(tokens, node)
        otherwise = parse(tokens, node)
        node.children = [condition, then, otherwise]
        return node
    raise ValueError(f"Unknown indicator {indicator}")


def step(node):
    """ Single step of execution, returning resulting node or None """
    if isinstance(node, Boolean):
        return None
    if isinstance(node, Variable):
        return node.lookup(node.token)
    if isinstance(node, Integer):
        return None
    if isinstance(node, String):
        return None
    if isinstance(node, Unary):
        expr = step(node.expr)
        if expr is not None:
            node.children[0] = expr
            node.children[0].parent = node
            return node
        if node.op == '-':  # Only cancel out, no actual negation
            if node.expr.token == 'U-':
                node.expr.expr.substitutions.update(node.expr.substitutions)
                node.expr.expr.substitutions.update(node.substitutions)
                node.expr.expr.parent = node.parent
                return node.expr.expr
            return None  # No other integer negations
        if node.op == '!':
            assert isinstance(node.expr, Boolean), node.expr
            return Boolean('T' if node.expr.token == 'F' else 'F', parent=node.parent, substitutions=node.substitutions)
        if node.op == '#':
            assert isinstance(node.expr, String), node.expr
            token = 'I' + node.expr.body
            return Integer(token, parent=node.expr.parent, substitutions=node.expr.substitutions)
        if node.op == '$':
            assert isinstance(node.expr, Integer), node.expr
            token = 'S' + node.expr.body
            return String(token, parent=node.expr.parent, substitutions=node.expr.substitutions)
    if isinstance(node, Lambda):
        return None
    if isinstance(node, Binary):
        right = step(node.right)
        if right is not None:
            node.children[1] = right
            node.children[1].parent = node
            return node
        left = step(node.left)
        if left is not None:
            node.children[0] = left
            node.children[0].parent = node
            return node
        if node.op in '+*':
            assert isinstance(node.right, Integer), node.right
            assert isinstance(node.left, Integer), node.left
            if node.op == '+':
                return Integer(node.left.token + '+++' + node.right.token, parent=node.parent, substitutions=node.substitutions)
            if node.op == '*':
                return Integer(node.left.token + '***' + node.right.token, parent=node.parent, substitutions=node.substitutions)
            raise ValueError(f"unknown math op {node.op}")
        if node.op == '=':
            if isinstance(node.left, Variable) or isinstance(node.right, Variable):
                if node.left.token == node.right.token:
                    return Boolean('T', parent=node.parent, substitutions=node.substitutions)
                return None
            assert isinstance(node.right, (Boolean, Integer, String)), node.right
            assert type(node.right) == type(node.left), f"{type(node.left)} {type(node.right)} dump {node.dump()}"
            token = 'T' if node.left.token == node.right.token else 'F'
            return Boolean(token, parent=node.parent, substitutions=node.substitutions)
        if node.op == '$':
            assert isinstance(node.right, Node), node.right
            assert isinstance(node.left, Lambda), node.left
            var = node.left.var
            expr = node.left.expr
            replace = node.right
            if expr.lookup(var) is not None:
                new_var = f"v{random.randint(100_000, 999_999)}"
                print(f"Renaming {var} to {new_var} in {expr.dump()}")
                expr.rename(var, new_var)
                print(f"Renamed {var} to {new_var} in {expr.dump()}")
                var = new_var
            assert expr.lookup(var) is None, f"{var} in expr {expr.dump()}"
            expr.substitutions[var] = replace
            expr.parent = node.parent
            return expr
        raise ValueError(f"Unknown binary op {node.op}")
    if isinstance(node, Conditional):
        condition = step(node.condition)
        if condition is not None:
            node.children[0] = condition
            node.children[0].parent = node
            return node
        if not isinstance(node.condition, Boolean):
            return None
        if node.condition.token == 'T':
            then = step(node.then)
            if then is not None:
                node.children[1] = then
                node.children[1].parent = node
                return node
            node.then.parent = node.parent
            return node.then
        else:
            otherwise = step(node.otherwise)
            if otherwise is not None:
                node.children[2] = otherwise
                node.children[2].parent = node
                return node
            node.otherwise.parent = node.parent
            return node.otherwise
        return None
    raise ValueError(f"Unknown node {type(node)}")


s = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
s = open('./language_test.txt').read()
# s = 'B$ La ? B= va Sy I1 I2 Sy'
s = 'B$ B$ L" B$ L# B$ v" B$ v# v# L# B$ v" B$ v# v# L" L# ? B= v# I! I" B$ L$ B+ B$ v" v$ B$ v" v$ B- v# I" I%'
s = 'U- U- I5'
tokens = s.strip().split()
tree = parse(tokens, None)
tree.check()

for _ in range(10):
    print(tree.dump())
    tree = step(tree)
    if tree is None:
        break