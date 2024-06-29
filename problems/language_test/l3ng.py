#!/usr/bin/env python
#%%

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

import math

def truncdiv(a, b):
    return math.trunc(a / b)

def truncmod(a, b):
    return a - b * truncdiv(a, b)

test_path = 'language_test.txt'
with open(test_path, 'r') as file:
    language_test = file.read()


def c2b94(s):
    value = 0
    for c in s:
        value *= 94
        value += ord(c) - 33
    return value


def b942c(value):
    s = ""
    while value:
        value, r = divmod(value, 94)
        s = chr(r + 33) + s
    return s

assert c2b94("/6") == 1337
assert b942c(1337) == "/6"


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


def tokenize(s):
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert len(s) > 0, f"Expected non-empty string, got {s}"
    return s.strip().split()


def parse(tokens):
    assert isinstance(tokens, list), f"Expected list, got {type(tokens)}"
    assert len(tokens) > 0, f"Expected non-empty list, got {tokens}"
    token, *remainder = tokens
    indicator, body = token[0], token[1:]
    if indicator in ["T", "F"]:
        assert not body, f"Expected empty body, got {body}"
        return token, remainder
    if indicator == "I":
        assert body, f"Expected non-empty body, got {body}"
        return token, remainder
    if indicator == "S":
        assert body, f"Expected non-empty body, got {body}"
        return token, remainder
    if indicator == "U":
        assert body in ("-", "!", "#", "$"), f"Expected -/!/#/$, got {body}"
        value, remainder = parse(remainder)
        return (token, value), remainder
    if indicator == "B":
        assert body in ("+", "-", "*", "/", "%", "<", ">", "=", "|", "&", ".", "T", "D", "$"), f"Expected +,-,*,/,%,<,>,=,|,&,.,T,D,$, got {body}"
        value1, remainder = parse(remainder)
        value2, remainder = parse(remainder)
        return (token, value1, value2), remainder
    if indicator == "?":
        assert not body, f"Expected empty body, got {body}"
        value1, remainder = parse(remainder)
        value2, remainder = parse(remainder)
        value3, remainder = parse(remainder)
        return (token, value1, value2, value3), remainder
    if indicator == "L":
        assert body, f"Expected non-empty body, got {body}"
        value, remainder = parse(remainder)
        return (token, value), remainder
    if indicator == "v":
        assert body, f"Expected non-empty body, got {body}"
        return token, remainder
    raise ValueError(f"Unknown indicator {indicator}")


assert parse(tokenize("T")) == ("T", [])
assert parse(tokenize("F")) == ("F", [])
assert parse(tokenize("I/6")) == ("I/6", [])
assert parse(tokenize("SB%,,/}Q/2,$_")) == ("SB%,,/}Q/2,$_", [])
assert parse(tokenize("U- I$")) == (("U-", "I$"), [])
assert parse(tokenize("U! T")) == (("U!", "T"), [])
assert parse(tokenize("U# S4%34")) == (("U#", "S4%34"), [])
assert parse(tokenize("U$ I4%34")) == (("U$", "I4%34"), [])
assert parse(tokenize("B+ I# I$")) == (("B+", "I#", "I$"), [])
assert parse(tokenize("B- I$ I#")) == (("B-", "I$", "I#"), [])
assert parse(tokenize("B* I$ I#")) == (("B*", "I$", "I#"), [])
assert parse(tokenize("B/ U- I( I#")) == (("B/", ("U-", "I("), "I#"), [])
assert parse(tokenize("B% U- I( I#")) == (("B%", ("U-", "I("), "I#"), [])
assert parse(tokenize("B< I$ I#")) == (("B<", "I$", "I#"), [])
assert parse(tokenize("B> I$ I#")) == (("B>", "I$", "I#"), [])
assert parse(tokenize("B= I$ I#")) == (("B=", "I$", "I#"), [])
assert parse(tokenize("B| T F")) == (("B|", "T", "F"), [])
assert parse(tokenize("B& T F")) == (("B&", "T", "F"), [])
assert parse(tokenize("B. S4% S34")) == (("B.", "S4%", "S34"), [])
assert parse(tokenize("BT I$ S4%34")) == (("BT", "I$", "S4%34"), [])
assert parse(tokenize("BD I$ S4%34")) == (("BD", "I$", "S4%34"), [])
assert parse(tokenize("B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK")) == (("B$", ("B$", ("L#", ("L$", "v#")), ("B.", "SB%,,/", "S}Q/2,$_")), "IK"), [])



def replace(expression, variable, replacement):
    """ Recursively replace variable with replacement in expression """
    assert isinstance(variable, str), f"Expected str, got {type(variable)}"
    assert isinstance(replacement, (str, tuple, bool, int)), f"{replacement}"
    if isinstance(expression, str):
        return replacement if expression == variable else expression
    if isinstance(expression, tuple):
        if len(expression) == 2 and expression[0] == "L" + variable[1:]:
                return expression
        return tuple(replace(e, variable, replacement) for e in expression)
    raise ValueError(f"Unknown expression type {expression}")


def evaluate(parsed):
    if isinstance(parsed, str):
        indicator, body = parsed[0], parsed[1:]
        if indicator in ("T", "F"):
            return True if indicator == "T" else False
        if indicator == "I":
            return c2b94(body)
        if indicator == "S":
            return decode(body)
        if indicator == "v":
            # These are parsed by "B$"
            return parsed
        raise ValueError(f"Unknown str indicator {indicator}")
    elif isinstance(parsed, tuple):
        token, *args = parsed
        indicator, body = token[0], token[1:]
        if indicator == "U":
            assert len(args) == 1, f"{parsed}"
            value = evaluate(args[0])
            if body == "-":
                assert isinstance(value, int), f"Expected int, got {type(value)} {value}"
                return -value
            if body == "!":
                assert isinstance(value, bool), f"Expected bool, got {type(value)} {value}"
                return not value
            if body == "#":
                assert isinstance(value, str), f"Expected str, got {type(value)} {value}"
                return c2b94(encode(value))
            if body == "$":
                assert isinstance(value, int), f"Expected int, got {type(value)} {value}"
                return decode(b942c(value))
            raise ValueError(f"Unknown unary {body}, {parsed}")
        if indicator == "B":
            assert len(args) == 2, f"{parsed}"
            value1 = evaluate(args[0])
            # Delay evaluation of arguments for lambda application
            value2 = evaluate(args[1]) if body != "$" else args[1]
            if body == "+":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return value1 + value2
            if body == "-":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return value1 - value2
            if body == "*":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return value1 * value2
            if body == "/":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return truncdiv(value1, value2)
            if body == "%":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return truncmod(value1, value2)
            if body == "<":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return value1 < value2
            if body == ">":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, int), f"Expected int, got {type(value2)} {value2}"
                return value1 > value2
            if body == "=":
                return value1 == value2
            if body == "|":
                assert isinstance(value1, bool), f"Expected bool, got {type(value1)} {value1}"
                assert isinstance(value2, bool), f"Expected bool, got {type(value2)} {value2}"
                return value1 or value2
            if body == "&":
                assert isinstance(value1, bool), f"Expected bool, got {type(value1)} {value1}"
                assert isinstance(value2, bool), f"Expected bool, got {type(value2)} {value2}"
                return value1 and value2
            if body == ".":
                assert isinstance(value1, str), f"Expected str, got {type(value1)} {value1}"
                assert isinstance(value2, str), f"Expected str, got {type(value2)} {value2}"
                return value1 + value2
            if body == "T":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, str), f"Expected str, got {type(value2)} {value2}"
                return value2[:value1]
            if body == "D":
                assert isinstance(value1, int), f"Expected int, got {type(value1)} {value1}"
                assert isinstance(value2, str), f"Expected str, got {type(value2)} {value2}"
                return value2[value1:]
            if body == "$":
                assert isinstance(value1, tuple), f"Expected tuple, got {type(value1)} {value1}"
                assert len(value1) == 2, f"Expected 2-tuple, got {len(value1)} {value1}"
                name, expr = value1
                assert isinstance(name, str), f"Expected str, got {type(name)} {name}"
                assert name.startswith("L"), f"Expected lambda, got {value1}"
                # Replace variable with second argument
                variable = "v" + name[1:]
                return evaluate(replace(expr, variable, value2))
        if indicator == "?":
            assert len(args) == 3, f"{parsed}"
            condition = evaluate(args[0])
            assert isinstance(condition, bool), f"Expected bool, got {type(condition)} {condition}"
            if condition:
                return evaluate(args[1])
            else:
                return evaluate(args[2])
        if indicator == "L":
            # These are parsed by "B$"
            assert len(args) == 1, f"{parsed}"
            return parsed
        raise ValueError(f"Unknown tuple indicator {indicator}")
    else:
        raise ValueError(f"Unknown parsed type {parsed}")


def ept(s):
    parsed, remainder = parse(tokenize(s))
    assert remainder == [], f"Expected empty remainder, got {remainder}"
    return evaluate(parsed)


assert ept("T") == True
assert ept("F") == False
assert ept("I/6") == 1337
assert ept("SB%,,/}Q/2,$_") == "Hello World!"
assert ept("U- I$") == -3
assert ept("U! T") == False
assert ept("U# S4%34") == 15818151
assert ept("U$ I4%34") == "test"
assert ept("B+ I# I$") == 5
assert ept("B- I$ I#") == 1
assert ept("B* I$ I#") == 6
assert ept("B/ U- I( I#") == -3
assert ept("B% U- I( I#") == -1
assert ept("B< I$ I#") == False
assert ept("B> I$ I#") == True
assert ept("B= I$ I#") == False
assert ept("B| T F") == True
assert ept("B& T F") == False
assert ept("B. S4% S34") == "test"
assert ept("BT I$ S4%34") == "tes"
assert ept("BD I$ S4%34") == "t"
assert ept("B$ B$ L# L$ v# B. SB%,,/ S}Q/2,$_ IK") == "Hello World!"
assert ept("? B> I# I$ S9%3 S./") == 'no'

# %%
import os
import requests

post_addr = "https://boundvariable.space/communicate"
# Authorization header
auth_path = '../../misc/SUBMISSION_HEADER.txt'
with open(auth_path, 'r') as file:
    auth = file.read()
assert auth.startswith("Authorization: Bearer ")
# convert to dict for requests
auth = {"Authorization": auth.lstrip("Authorization: ").strip()}

path = 'language_test.txt'
if not os.path.exists(path) or True:
    data = 'S' + encode('get language_test')
    response = requests.post(post_addr, headers=auth, data=data)
    response.raise_for_status()
    language_test = response.text.strip()
    with open(path, 'w') as file:
        file.write(language_test)
with open(path, 'r') as file:
    language_test = file.read()
print(language_test)

print(ept(language_test))