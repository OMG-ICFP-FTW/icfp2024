#!/usr/bin/env python
#%%
from dataclasses import 
from pprint import pprint
import random


def tokenize(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert len(s) > 0, f"Expected non-empty string, got {s}"
    return s.strip().split()


def untokenize(tokens):
    assert isinstance(tokens, list), f"Expected list, got {type(tokens)}"
    assert len(tokens) > 0, f"Expected non-empty list, got {tokens}"
    assert all(isinstance(t, str) for t in tokens), f"Expected list of str, got {tokens}"
    return " ".join(tokens)


def parse(tokens):
    assert isinstance(tokens, list), f"Expected list, got {type(tokens)}"
    assert len(tokens) > 0, f"Expected non-empty list, got {tokens}"
    token, *remainder = tokens
    indicator, body = token[0], token[1:]
    if indicator == "I":
        assert body, f"Expected non-empty body, got {body}"
        return token, remainder
    if indicator == "B":
        assert body == '$', f"Expected body $, got {body}"
        value1, remainder = parse(remainder)
        value2, remainder = parse(remainder)
        return (token, value1, value2), remainder
    if indicator == "L":
        assert body, f"Expected non-empty body, got {body}"
        value, remainder = parse(remainder)
        return (token, value), remainder
    if indicator == "v":
        assert body, f"Expected non-empty body, got {body}"
        return token, remainder
    raise ValueError(f"Unknown indicator {indicator}")


def unparse(parsed, remainder=None):
    remainder = [] if remainder is None else remainder
    assert isinstance(remainder, list), f"Expected list, got {type(remainder)}"
    if isinstance(parsed, str):
        assert parsed, f"Expected non-empty str, got {parsed}"
        return [parsed] + remainder
    if isinstance(parsed, tuple):
        assert len(parsed) > 0, f"Expected non-empty tuple, got {parsed}"
        if len(parsed) == 1:
            return unparse(parsed[0], remainder)
        return unparse(parsed[0], unparse(parsed[1:], remainder))
    raise ValueError(f"Unknown parsed type {parsed}")

s = "B$ Lx vx I1"
s = "B$ Lx B$ Ly vx I1 I2"
assert untokenize(unparse(*parse(tokenize(s)))) == s


def step(parsed, substitutions):
    """ Perform a single step of evaluation """
    assert isinstance(parsed, tuple), f"Expected tuple, got {type(parsed)}"
    first = parsed[0]
    if isinstance(first, tuple):
        # recurse into first element
        return (step(first, substitutions), *parsed[1:])
    if isinstance(first, str):
        indicator, body = first[0], first[1:]
        if indicator == "I":
            print("INT", body, "Nothing to do!")
            return parsed
        if indicator == "v":
            assert first in substitutions, f"Expected substitution, got {first}"
            return substitutions[first]
        if indicator == "L":
            assert len(parsed) == 2, f"Expected 2-tuple, got {len(parsed)} {parsed}"
            print("LAMBDA", body, "Nothing to do!")
            return parsed
        if indicator == "B":
            assert body == '$', f"Expected body $, got {body}"
            _, expression, replacement = parsed
            assert isinstance(expression, tuple), f"Expected tuple, got {type(expression)}"
            assert isinstance(expression[0], str), f"Expected str, got {type(expression[0])}"
            assert expression[0].startswith("L"), f"Expected lambda, got {expression[0]}"
            exprtoken, exprbody = expression
            varname = "v" + exprtoken[1:]
            assert len(varname) > 1, f"Expected non-empty name, got {varname}"
            # Check if the name is already in our list of substitutions
            if varname in substitutions:
                # If so, pre-process the expression to replace the name with the substitution
                new_varname = varname + str(random.randint(0, 9999))
                assert new_varname not in substitutions, f"Expected new name, got {new_varname}"
                new_exprbody = replace(exprbody, varname, new_varname)
                # Swap them in
                varname, exprbody = new_varname, new_exprbody
            # Add the substitution to our list
            substitutions[varname] = replacement
            # Return the inner expression with the substitution
            return exprbody
        raise ValueError(f"Unknown first indicator {indicator}")
    raise ValueError(f"Unknown first type {type(first)}")

 
assert step(('v1',), {'v1': ('I1',)}) == ('I1',)
expr = ('B$', ('Lx', 'vx'), ('I1',))
subs = {}
print('start')
print('expr', expr)
print('subs', subs)
print('step')
expr = step(expr, subs)
print('expr', expr)
print('subs', subs)
print('step')
expr = step(expr, subs)
print('expr', expr)
print('subs', subs)

# %%

def replace(expression, variable, replacement):
    """ Recursively replace variable with replacement in expression """
    assert isinstance(variable, str), f"Expected str, got {type(variable)}"
    assert isinstance(replacement, (str, tuple, bool, int)), f"{replacement}"
    if isinstance(expression, (str, int, bool)):
        return replacement if expression == variable else expression
    if isinstance(expression, tuple):
        return tuple(replace(e, variable, replacement) for e in expression)
    raise ValueError(f"Unknown expression type {expression}")
