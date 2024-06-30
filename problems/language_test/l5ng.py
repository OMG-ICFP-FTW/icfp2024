#!/usr/bin/env python
# %%

"""
I Can Finally Publish

Core data type:  ICFP
- String (not yet tokenized)
- Token (recognized, but not yet parsed)
- Expression (parsed and nested objects, with substitutions)

ICFP.remainder - remaining string
ICFP.tokens - list of unconsumed tokens
ICFP.expression - parsed expression, grouped but not yet evaluated
ICFP.substitutions - dict of var name -> expression


B$ L# B$ L" B+ v" v" B* I$ I# v8
B$ L" B+ v" v" B* I$ I#
B+ B* I$ I# B* I$ I#
B+ I' B* I$ I#
B+ I' I'
I-


"""
from typing import Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Expression:
    token: str
    arguments: Tuple['Expression'] = field(default_factory=tuple)
    substitutions: dict = field(default_factory=dict)
    parent: Optional['Expression'] = None

    def all_vars(self):
        return set()

    def lookup(self, var):
        print("Lookup for", var, "in", self)
        assert isinstance(var, VariableExpr), f"{var}"
        if var in self.substitutions:
            return self.substitutions[var]
        print("going to parent", self.parent.dump())
        print("parent type", type(self.parent))
        print("parent has substitutions", self.parent.substitutions)
        return self.parent.lookup(var)

    def dump(self):
        s = self.token
        for arg in self.arguments:
            s += " " + arg.dump()
        if self.substitutions:
            s += " {"
            for var, expr in self.substitutions.items():
                s += f"{var.token}: {expr.dump()}, "
            s += "}"
        return s


@dataclass
class IntegerExpr(Expression):
    def __post_init__(self):
        assert len(self.arguments) == 0, f"{self}"
        assert self.token[0] == "I", f"{self}"
        assert len(self.token) > 1, f"{self}"


@dataclass
class VariableExpr(Expression):
    def __post_init__(self):
        assert len(self.arguments) == 0, f"{self}"
        assert self.token[0] == "v", f"{self}"
        assert len(self.token) > 1, f"{self}"

    def all_vars(self):
        return {self.token}
    
    def eval(self):
        value = self.lookup(self)
        assert isinstance(value, Expression), f"{value}"
        return value
    
    def __str__(self):
        return self.token

    def __hash__(self):
        return hash(self.token)


@dataclass
class LambdaExpr(Expression):
    def __post_init__(self):
        assert len(self.arguments) == 1, f"{self}"

    def all_vars(self):
        vars = set()
        vars.add(self.var.token)
        vars.update(self.body.all_vars())
        return vars

    @property
    def body(self):
        return self.arguments[0]
    
    @property
    def var(self):
        return VariableExpr('v' + self.token[1:])


@dataclass
class BinaryExpr(Expression):
    def __post_init__(self):
        assert len(self.arguments) == 2, f"{self}"

    def all_vars(self):
        vars = set()
        for arg in self.arguments:
            vars.update(arg.all_vars())
        return vars

    @property
    def left(self):
        return self.arguments[0]
    
    @property
    def right(self):
        return self.arguments[1]
    
    def eval(self):
        _, op = self.token
        if op in "+*":
            right = self.right.eval()
            assert isinstance(right, IntegerExpr), f"{right}"
            left = self.left.eval()
            assert isinstance(left, IntegerExpr), f"{left}"
            if op == "+":
                return IntegerExpr(left.token + "+++" + right.token)
            if op == "*":
                return IntegerExpr(left.token + "***" + right.token)
        if op in '$':
            assert isinstance(self.left, LambdaExpr), f"{self}"
            lambda_var = self.left.var
            lambda_body = self.left.body
            assert isinstance(lambda_body, Expression), f"{self}"
            # TODO: handle this by renaming
            assert lambda_var not in self.right.all_vars(), f"{self}"
            lambda_body.substitutions[lambda_var] = self.right
            print("Evaluating application, var", lambda_var, "body", lambda_body.dump(), "value", self.right.dump())
            return lambda_body
        raise ValueError(f"Unknown operator {op}")


@dataclass
class ICFP:
    remainder: str
    tokens: list = field(default_factory=list)
    expression: object = field(init=False)
    substitutions: dict = field(default_factory=dict)

    def __post_init__(self):
        self.expression = self.parse()

    def lookup(self, var):
        assert isinstance(var, VariableExpr), f"{var}"
        if var in self.substitutions:
            return self.substitutions[var]
        raise ValueError(f"Variable not found {var}")

    def pop_token(self):
        """ Pop the next token from the list """
        if len(self.tokens):
            return self.tokens.pop(0)
        assert self.remainder, "No more string to tokenize"
        parts = self.remainder.split(maxsplit=1) 
        self.remainder = parts[1] if len(parts) > 1 else ""
        return parts[0]

    def parse(self, parent):
        """ Parse the tokens into an expression """
        first = self.pop_token()
        if first[0] == "I":
            return IntegerExpr(first, parent=parent)
        if first[0] == "v":
            return VariableExpr(first, parent=parent)
        if first[0] == "L":
            expr = LambdaExpr(first, (self.parse(None),), parent=parent)
            expr.
            return expr
        if first[0] == "B":
            return BinaryExpr(first, (self.parse(), self.parse()), parent=parent)
        raise ValueError(f"Invalid token {first}")

    def step(self):
        """ Single step of evaluation """
        self.expression = self.expression.eval()
    
    def dump(self):
        return self.expression.dump()


icfp = ICFP('B$ L# B$ L" B+ v" v" B* I$ I# v8')
print(icfp.dump())
print(icfp.step())
print(icfp.dump())
print(icfp.step())
print(icfp.dump())
print(icfp.step())
print(icfp.dump())
