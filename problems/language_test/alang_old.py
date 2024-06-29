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


from dataclasses import dataclass, field

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



@dataclass
class Token:
    s: str

    @property
    def indicator(self):
        return self.s[0]
    
    @property
    def body(self):
        return self.s[1:]


@dataclass
class Boolean(Token):
    """
    indicator = T and an empty body represents the constant true, and indicator = F and an empty body represents the constant false.
    """
    def __post_init__(self):
        assert self.indicator in ["T", "F"], f"Expected T or F, got {self.indicator}"
        assert not self.body, f"Expected empty body, got {self.body}"

    def __bool__(self):
        return self.indicator == "T"


assert bool(Boolean('T')) == True
assert bool(Boolean('F')) == False


@dataclass
class Integer(Token):
    """
    indicator = I, requires a non-empty body.

    The body is interpreted as a base-94 number, e.g. the digits are the 94 printable ASCII characters with the exclamation mark representing 0, double quotes 1, etc. For example, I/6 represent the number 1337.
    """
    def __post_init__(self):
        assert self.indicator == "I", f"Expected I, got {self.indicator}"
        assert self.body, f"Expected non-empty body, got {self.body}"

    def __int__(self):
        return c2b94(self.body)


assert int(Integer('I/6')) == 1337


str_reference = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`|~ \n"
decode_map = {chr(k): v for (k, v) in zip(list(range(33,33 + len(str_reference))),str_reference)}
encode_map = {v: k for (k, v) in decode_map.items()}
decode_trans = str.maketrans(decode_map)
encode_trans = str.maketrans(encode_map)


@dataclass
class String(Token):
    """
    indicator = S

    The Cult of the Bound variable seems to use a system similar to ASCII to encode characters, but ordered slightly differently. Specifically, ASCII codes 33 to 126 from the body can be translated to human readable text by converting them according to the following order:

    abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!"#$%&'()*+,-./:;<=>?@[\\]^_`|~<space><newline>

    Here <space> denotes a single space character, and <newline> a single newline character. For example, SB%,,/}Q/2,$_ represents the string "Hello World!".
    """

    def __post_init__(self):
        assert self.indicator == "S", f"Expected S, got {self.indicator}"
        assert self.body, f"Expected non-empty body, got {self.body}"

    def decode(self):
        return self.body.translate(decode_trans)

    @classmethod
    def encode(cls, s):
        return "S" + s.translate(encode_trans)


assert String('SB%,,/}Q/2,$_').decode() == "Hello World!"
assert String.encode("Hello World!") == "SB%,,/}Q/2,$_"


@dataclass
class Unary(Token):
    """
    indicator = U, requires a body of exactly 1 character long, and should be followed by an ICFP which can be parsed from the tokens following it.
    """
    def __post_init__(self):
        assert self.indicator == "U", f"Expected U, got {self.indicator}"
        assert len(self.body) == 1, f"Expected body of length 1, got {self.body}"
        assert self.body in ["-", "!", "#", "$"], f"Expected one of -, !, #, $, got {self.body}"


@dataclass
class Binary(Token):
    """
    indicator = B, requires a body of exactly 1 character long, and should be followed by two ICFPs (let's call them x and y).
    """
    def __post_init__(self):
        assert self.indicator == "B", f"Expected B, got {self.indicator}"
        assert len(self.body) == 1, f"Expected body of length 1, got {self.body}"
        assert self.body in ["+", "-", "*", "/", "%", "<", ">", "=", "|", "&", ".", "T", "D", "$"], f"Expected one of +, -, *, /, %, <, >, =, |, &, ., T, D, $, got {self.body}"


@dataclass
class If(Token):
    """
    indicator = ? with an empty body, followed by three ICFPs: the first should evaluate to a boolean, if it's true then the second is evaluated for the result, else the third.
    """
    def __post_init__(self):
        assert self.indicator == "?", f"Expected ?, got {self.indicator}"
        assert not self.body, f"Expected empty body, got {self.body}"


@dataclass
class Lambda(Token):
    """
    indicator = L is a lambda abstraction, where the body should be interpreted as a base-94 number in the same way as integers, which is the variable number, and it takes one ICFP as argument.
    """
    value: int = field(init=False)
    def __post_init__(self):
        assert self.indicator == "L", f"Expected L, got {self.indicator}"
        assert self.body, f"Expected non-empty body, got {self.body}"
        self.value = c2b94(self.body)

@dataclass
class Variable(Token):
    """
    indicator = v is a variable, with again a body being the base-94 variable number.
    """
    value: int = field(init=False)
    def __post_init__(self):
        assert self.indicator == "v", f"Expected v, got {self.indicator}"
        assert self.body, f"Expected non-empty body, got {self.body}"
        self.value = c2b94(self.body)


def parse(s):
    """ Parse single token """
    assert isinstance(s, str), f"Expected string, got {type(s)}"
    assert len(s), f"Expected string of length, got {s}"
    assert len(s.split()) == 1, f"Expected single token, got {s}"

    indicator = s[0]
    if indicator in ["T", "F"]:
        return Boolean(s)
    if indicator == "I":
        return Integer(s)
    if indicator == "S":
        return String(s)
    if indicator == "U":
        return Unary(s)
    if indicator == "B":
        return Binary(s)
    if indicator == "?":
        return If(s)
    if indicator == "L":
        return Lambda(s)
    if indicator == "v":
        return Variable(s)
    raise ValueError(f"Unknown token {s}")


def evaluate(tokens):
    if isinstance(tokens[0], (Boolean, Integer, String)):
        return tokens[0], tokens[1:]
    raise ValueError(f"Cannot (yet) start program with {tokens[0]}")


assert evaluate([Boolean('T')]) == (Boolean('T'), [])
assert evaluate([Integer('I/6')]) == (Integer('I/6'), [])



#     def evaluate(self, tokens):
#         if self.body == "-":
#             value, tokens = tokens.pop(0).evaluate(tokens)
#             assert isinstance(value, ), f"Expected int, got {type(value)}"
#             return -value, tokens
#         if self.body == "!":
#             value, tokens = tokens.pop(0).evaluate(tokens)
#             assert isinstance(value, bool), f"Expected bool, got {type(value)}"
#             return not value, tokens
#         if self.body == "#":
#             print("String to int", tokens)
#             value, tokens = tokens.pop(0).evaluate(tokens)
#             assert isinstance(value, str), f"Expected str, got {type(value)}"
#             print("String to int", value)
#             return c2b94(value), tokens
#         if self.body == "$":
#             value, tokens = tokens.pop(0).evaluate(tokens)
#             assert isinstance(value, int), f"Expected int, got {type(value)}"
#             return b942c(value), tokens
#         raise ValueError(f"Unknown unary operator {self.body}")
    

# assert Unary('U-').evaluate([Integer('I$')]) == (-3, [])
# assert Unary('U!').evaluate([Boolean('T')]) == (False, [])
# assert Unary('U#').evaluate([String('S4%34')]) == (15818151, [])
# assert Unary('U$').evaluate([Integer('I4%34')]) == ('test', [])


# assert Program.from_string("T").evaluate() == True