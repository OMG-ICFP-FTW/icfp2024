from typing import Union

from dataclasses import dataclass

from icfp_lang import strings


class String:
    @staticmethod
    def parse(source: str) -> 'Value':
        return Value(strings.decode(source))


class Integer:
    @staticmethod
    def parse(source: str) -> 'Value':
        raise NotImplemented('Base94 integer parsing is not yet implemented')


class Boolean:
    @staticmethod
    def parse(source: str) -> 'Value':
        return Value(source == 'T')

value_parse_lookup = {
    'S': String,
    'I': Integer,
    'T': Boolean,
    'F': Boolean,
}

@dataclass
class Value:
    val: Union[int, bool, str]

    @staticmethod
    def parse(source: str) -> 'Value':
        value_parse_lookup[source[0]](source)


class UnaryOp:
    pass


class Neg(UnaryOp):
    symbol = '-'

    @staticmethod
    def apply(val: Value) -> Value:
        Value(-val.val)


class Not(UnaryOp):
    symbol = '!'

    @staticmethod
    def apply(val: Value) -> Value:
        return Value(not val.val)


class StrToInt(UnaryOp):
    symbol = '#'

    @staticmethod
    def apply(val: Value) -> Value:
        Value(int(val.val))


class IntToStr(UnaryOp):
    symbol = '$'

    @staticmethod
    def apply(val: Value) -> Value:
        Value(str(val.val))


@dataclass
class Unary:
    op: Union[Neg, Not, StrToInt, IntToStr]
    val: Value

    def apply(self) -> Value:
        return self.op.apply(self.val)


class BinaryOp:
    # + Integer addition    B+ I# I$ -> 5
    # - Integer subtraction B- I$ I# -> 1
    # * Integer multiplication  B* I$ I# -> 6
    # / Integer division (truncated towards zero)   B/ U- I( I# -> -3
    # % Integer modulo  B% U- I( I# -> -1
    # < Integer comparison  B< I$ I# -> false
    # > Integer comparison  B> I$ I# -> true
    # = Equality comparison, works for int, bool and string B= I$ I# -> false
    # | Boolean or  B| T F -> true
    # & Boolean and B& T F -> false
    # . String concatenation    B. S4% S34 -> "test"
    # T Take first x chars of string y  BT I$ S4%34 -> "tes"
    # D Drop first x chars of string y  BD I$ S4%34 -> "t"
    # $ Apply term x to y (see Lambda abstractions)
    pass


class Add(BinaryOp):
    symbol = '+'

    @staticmethod
    def apply(first: Value, second: Value) -> Value:
        Value(first.val + second.val)


class Sub(BinaryOp):
    symbol = '-'

    @staticmethod
    def apply(first: Value, second: Value) -> Value:
        Value(first.val - second.val)


@dataclass
class Binary:
    op: Union[Add, Sub]
    first: Value
    second: Value

    def apply(self) -> Value:
        return self.op.apply(self.first, self.second)


Expr = Union[Value, Unary, Binary]

prefixes = {
    'S': String,
    'B': Boolean,
}

@dataclass
class Program:
    """A program in Interstellar Communication Functional Program (ICFP)"""
    expr: Expr

    @staticmethod
    def parse(source: str) -> 'Program':
        pass


def encode(pgm: Program) -> str:
    """Serialize a program to the ICFP encoding"""
    if isinstance(pgm.expr, Value) and isinstance(pgm.expr.val, str):
        return strings.encode(pgm.expr.val)
    else:
        raise ValueError('ICFP Program structure not recognized')


def decode(string: str) -> Program:
    """Serialize a program to the ICFP encoding"""
    return Program(Value(strings.decode(string)))


def human_readable(pgm: Program) -> str:
    if isinstance(pgm.expr, Value) and isinstance(pgm.expr.val, str):
        return pgm.expr.val
    else:
        raise ValueError('ICFP Program structure not recognized')
