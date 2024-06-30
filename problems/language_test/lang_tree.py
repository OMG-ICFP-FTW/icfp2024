#!/usr/bin/env python
# %%
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass, field

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
                s += f" {k}: <{v.dump()}>,"
            s += "}"
        return s


@dataclass
class Boolean(Node):
    def check(self):
        assert self.indicator in ('T', 'F'), self
        assert not len(self.body), self
        assert self.children is None, self

    def eval(self):
        return self


@dataclass
class Variable(Node):
    def check(self):
        assert self.indicator == "v", self
        assert len(self.body), self
        assert self.children is None, self

    def __hash__(self):
        return hash(self.token)
    
    def eval(self):
        return self.lookup(self.token)
    

@dataclass
class Integer(Node):
    def check(self):
        assert self.indicator == "I", self
        assert len(self.body), self
        assert self.children is None, self
    
    def eval(self):
        return self
    

@dataclass
class String(Node):
    def check(self):
        assert self.indicator == "S", self
        assert len(self.body), self
        assert self.children is None, self

    def eval(self):
        return self


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

    def eval(self):
        return self


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
        assert self.op in "+*=$", self
        assert len(self.children) == 2, self
        assert all(c.parent == self for c in self.children), self
        self.left.check()
        self.right.check()

    def eval(self):
        if self.op in '+*':
            right = self.right.eval()
            assert isinstance(right, Integer), right
            left = self.left.eval()
            assert isinstance(left, Integer), left
            if self.op == '+':
                return Integer(left.token + '+++' + right.token, parent=self.parent)
            if self.op == '*':
                return Integer(left.token + '***' + right.token, parent=self.parent)
        if self.op == '$':
            left = self.left.eval()
            assert isinstance(left, Lambda), left
            var = self.left.var
            expr = self.left.expr
            replace = self.right
            assert expr.lookup(var) is None, self
            expr.substitutions[var] = replace
            expr.parent = self.parent
            return expr
        raise ValueError(f"unknown op {self.op}")


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

    def eval(self):
        condition = self.condition.eval()
        assert isinstance(condition, Integer), condition
        if condition.body == '1':
            return self.then.eval()
        return self.otherwise.eval()


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
    if node.indicator in 'IL':
        return None
    if isinstance(node, Variable):
        return node.lookup(node.token)
    if isinstance(node, Binary):
        right = step(node.right)
        if right is not None:
            node.children[1] = right
            return node
        left = step(node.left)
        if left is not None:
            node.children[0] = left
            return node
        if node.op in '+*':
            assert isinstance(node.right, Integer), node.right
            assert isinstance(node.left, Integer), node.left
            if node.op == '+':
                return Integer(node.left.token + '+++' + node.right.token, parent=node.parent, substitutions=node.substitutions)
            if node.op == '*':
                return Integer(node.left.token + '***' + node.right.token, parent=node.parent, substitutions=node.substitutions)
            raise ValueError(f"unknown math op {node.op}")
        if node.op == '$':
            assert isinstance(node.right, Node), node.right
            assert isinstance(node.left, Lambda), node.left
            var = node.left.var
            expr = node.left.expr
            replace = node.right
            assert expr.lookup(var) is None, f"{var} in expr {expr.dump()}"
            expr.substitutions[var] = replace
            expr.parent = node.parent
            return expr
        raise ValueError(f"Unknown binary op {node.op}")


s = 'B$ L# B$ L" B+ v" v" B* I$ I# v8'
s = open('./language_test.txt').read()
tokens = s.strip().split()
tree = parse(tokens, None)
tree.check()

for _ in range(10):
    print(tree.dump())
    tree = step(tree)
    if tree is None:
        break