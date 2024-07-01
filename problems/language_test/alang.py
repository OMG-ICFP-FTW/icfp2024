#!/usr/bin/env python
#%%
from collections import defaultdict
from typing import List, Tuple, Union, Any, Optional, Dict
from dataclasses import dataclass, field
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

    @property
    def indicator(self) -> str:
        return self.token[0]
    
    @property
    def body(self) -> str:
        return self.token[1:]
    
    def leaf_eq(self, other: 'Node') -> bool:
        """ Simple test for leaf equality, false does not imply inequality """
        if self.indicator in 'TFvIS':
            return self.token == other.token
        return False
    
    def walk(self):
        yield self
        if self.children:
            for child in self.children:
                yield from child.walk()
    
    def dump(self):
        return ' '.join(n.token for n in self.walk())

    def copy(self):
        children = [c.copy() for c in self.children] if self.children else None
        return Node(self.token, children)

    def rename(self, old, new):
        if self.token == old:
            self.token = new
        elif self.indicator == 'L' and self.body == old[1:]:
            return
        if self.children:
            for c in self.children:
                c.rename(old, new)

    def match(self, pattern: 'Node') -> Optional[Dict[str, 'Node']]:
        ''' Return dict of placeholder matches or None '''
        if pattern.token in 'xyz':  # Placeholders
            return {pattern.token: self}
        if len(pattern.token) == 1:
            if pattern.indicator != self.indicator:
                return None
        elif pattern.token != self.token:
            return None
        matches = {}
        for sc, pc in zip(self.children or [], pattern.children or []):
            match = sc.match(pc)
            if match is None:
                return None
            matches.update(match)
        return matches
    
    def replace(self, pattern: 'Node', matches: Dict[str, 'Node']):
        """ in-place replacement of node with matched pattern """
        if pattern.token in 'xyz':  # placeholders
            node = matches.pop(pattern.token)
            self.token = node.token
            self.children = node.children
            return self
        # build in place
        self.token = pattern.token
        if pattern.children is None:
            self.children = None
            return self
        # build children
        self.children = []
        for pc in pattern.children:
            self.children.append(Node(pc.token).replace(pc, matches))
        return self


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


assert parse("I123").match(parse("I")) == {}
assert parse("I123").match(parse("x")) == {'x': parse("I123")}


PATTERNS_TEXT = """
# Unary operators cancel out
U! T -> F
U! F -> T
U- I! -> I!
U- U- x -> x
U! U! x -> x
U$ U# x -> x
U# U$ x -> x

# Boolean operators
B& T T -> T
B& T x -> x
B& x T -> x
B& F x -> F
B& x F -> F
B& U! x U! y -> U! B| x y
B| T x -> T
B| x T -> T
B| F F -> F
B| F x -> x
B| x F -> x
B| U! x U! y -> U! B& x y

# Arithmetic: Reduce and move negation higher
B+ x I! -> x
B+ I! x -> x
B- x I! -> x
B- I! x -> U- x
B+ x U- y -> B- x y
B- x U- y -> B+ x y
B* I! x -> I!
B* x I! -> I!
B* U- x y -> U- B* x y
B* x U- y -> U- B* x y
B* U- x U- y -> B* x y
B/ I! x -> I!
B/ U- x y -> U- B/ x y
B/ x U- y -> U- B/ x y

# Comparison - these have to be computed
B< U- x U- y -> B> x y
B> U- x U- y -> B< x y
B= U- x U- y -> B= x y

# Conditional
? T x y -> x
? F x y -> y
"""

@dataclass
class Rule:
    pattern: Node
    replace: Node

    @classmethod
    def from_line(cls, line: str):
        left, right = line.split('->')
        pattern, replace = parse(left), parse(right)
        return cls(pattern, replace)

    def match(self, node: Node):
        return node.match(self.pattern)
    
    def apply(self, node: Node, matches: Dict[str, Node]):
        node.replace(self.replace, matches)

    def __str__(self):
        return f"Rule({self.pattern.dump()} -> {self.replace.dump()})"


@dataclass
class StrToIntRule(Rule):
    pattern: Node = field(default_factory=lambda: parse('U# S'))
    replace: Node = field(default_factory=lambda: parse('x'))

    def apply(self, node: Node, matches: Dict[str, Node]):
        matches['x'] = Node('I' + node.children[0].body)
        node.replace(self.replace, matches)


@dataclass
class IntToStrRule(Rule):
    pattern: Node = field(default_factory=lambda: parse('U$ I'))
    replace: Node = field(default_factory=lambda: parse('x'))

    def apply(self, node: Node, matches: Dict[str, Node]):
        matches['x'] = Node('S' + node.children[0].body)
        node.replace(self.replace, matches)


@dataclass
class ArithmeticRule(Rule):
    replace: Node = field(default_factory=lambda: parse('x'))

    def apply(self, node: Node, matches: Dict[str, Node]):
        left, right = node.children
        a, b = c2b94(left.body), c2b94(right.body)
        c = self.func(a, b)
        matches['x'] = Node(f"I{b942c(c)}")
        node.replace(self.replace, matches)


@dataclass
class AdditionRule(ArithmeticRule):
    pattern: Node = field(default_factory=lambda: parse('B+ I I'))

    def func(self, a, b):
        return a + b
    

@dataclass
class SubtractionRule(ArithmeticRule):
    pattern: Node = field(default_factory=lambda: parse('B- I I'))

    def func(self, a, b):
        return a - b
    

@dataclass
class MultiplicationRule(ArithmeticRule):
    pattern: Node = field(default_factory=lambda: parse('B* I I'))

    def func(self, a, b):
        return a * b
    

@dataclass
class DivisionRule(ArithmeticRule):
    pattern: Node = field(default_factory=lambda: parse('B/ I I'))

    def func(self, a, b):
        return truncdiv(a, b)
    

@dataclass
class ModulusRule(ArithmeticRule):
    pattern: Node = field(default_factory=lambda: parse('B% I I'))

    def func(self, a, b):
        return truncmod(a, b)


@dataclass
class ComparisonRule(Rule):
    replace: Node = field(default_factory=lambda: parse('x'))

    def apply(self, node: Node, matches: Dict[str, Node]):
        left, right = node.children
        a, b = c2b94(left.body), c2b94(right.body)
        matches['x'] = Node("T" if self.func(a, b) else "F")
        node.replace(self.replace, matches)


@dataclass
class LessThanRule(ComparisonRule):
    pattern: Node = field(default_factory=lambda: parse('B< I I'))

    def func(self, a, b):
        return a < b

@dataclass
class GreaterThanRule(ComparisonRule):
    pattern: Node = field(default_factory=lambda: parse('B> I I'))

    def func(self, a, b):
        return a > b
    
@dataclass
class EqualsRule(ComparisonRule):
    pattern: Node = field(default_factory=lambda: parse('B= I I'))

    def func(self, a, b):
        return a == b


@dataclass
class EquivalenceRule(Rule):
    pattern: Node = field(default_factory=lambda: parse('B= x y'))
    replace: Node = field(default_factory=lambda: parse('T'))

    def match(self, node: Node):
        if self.pattern.token == node.token:
            left, right = node.children
            return {} if left.leaf_eq(right) else None
        return None


@dataclass
class ConcatenationRule(Rule):
    pattern: Node = field(default_factory=lambda: parse('B. S S'))
    replace: Node = field(default_factory=lambda: parse('x'))

    def apply(self, node: Node, matches: Dict[str, Node]):
        matches['x'] = Node('S' + node.children[0].body + node.children[1].body)
        node.replace(self.replace, matches)


@dataclass
class ApplicationRule(Rule):
    icfp: 'ICFP' = None
    pattern: Node = field(default_factory=lambda: parse('B$ L x y'))
    replace: Node = field(default_factory=lambda: parse('x'))

    def apply(self, node: Node, matches: Dict[str, Node]):
        old_var = 'v' + node.children[0].body
        new_var = self.icfp.new_var(matches.pop('y'))
        matches['x'].rename(old_var, new_var)
        node.replace(self.replace, matches)


@dataclass
class VariableRule(Rule):
    icfp: 'ICFP' = None
    pattern: Node = field(default_factory=lambda: parse('v'))
    replace: Node = field(default_factory=lambda: parse('x'))

    def match(self, node: Node):
        return {} if node.token in self.icfp.variables else None

    def apply(self, node: Node, matches: Dict[str, Node]):
        matches['x'] = self.icfp.variables[node.token].copy()
        node.replace(self.replace, matches)


@dataclass
class Affordance:
    node: Node
    rule: Rule
    matches: Dict[str, Node]

    def __str__(self):
        return f"Affordance({self.rule})"


@dataclass
class ICFP:
    root: Node
    variables: Dict[int, Node] = field(default_factory=dict)
    rules: Dict[str, List[Rule]] = field(default_factory=lambda: defaultdict(list))

    def __post_init__(self):
        if isinstance(self.root, str):
            self.root = parse(self.root)
        for line in PATTERNS_TEXT.strip().split('\n'):
            if line.strip() and not line.strip().startswith('#'):
                self.add_rule(Rule.from_line(line))
        self.add_rule(StrToIntRule())
        self.add_rule(IntToStrRule())
        self.add_rule(AdditionRule())
        self.add_rule(SubtractionRule())
        self.add_rule(MultiplicationRule())
        self.add_rule(DivisionRule())
        self.add_rule(ModulusRule())
        self.add_rule(LessThanRule())
        self.add_rule(GreaterThanRule())
        self.add_rule(EqualsRule())
        self.add_rule(EquivalenceRule())
        self.add_rule(ConcatenationRule())
        self.add_rule(ApplicationRule(icfp=self))
        self.add_rule(VariableRule(icfp=self))

    def add_rule(self, rule: Rule):
        self.rules[rule.pattern.token].append(rule)
    
    def new_var(self, node: Node) -> str:
        name = f'v{len(self.variables):09d}'
        self.variables[name] = node
        return name

    def get_affordances(self):
        affordances = [] # list of (node, rule, matches) tuple
        for node in self.root.walk():
            # Token specific rules and indicator generic rules
            for rule in self.rules[node.token] + self.rules[node.indicator]:
                matches = node.match(rule.pattern)
                if matches is not None:
                    affordance = Affordance(node, rule, matches)
                    affordances.append(affordance)
        return affordances
    
    def apply_affordance(self, affordance: Affordance):
        affordance.rule.apply(affordance.node, affordance.matches)

    def step(self):
        affordances = self.get_affordances()
        if not affordances:
            return False
        affordance = affordances[0]
        self.apply_affordance(affordance)
        return True

    def run(self):
        while self.step():
            pass
        return self.root


with open('language_test.txt') as f:
    language_test = f.read()

decode(ICFP(language_test).run().body)