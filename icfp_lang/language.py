from typing import Union

from dataclasses import dataclass

from icfp_lang import strings

@dataclass
class String:
    val: str


@dataclass
class Program:
    """A program in Interstellar Communication Functional Program (ICFP)"""
    val: Union[String]


def encode(pgm: Program) -> str:
    """Serialize a program to the ICFP encoding"""
    if pgm.val and isinstance(pgm.val, String):
        return strings.encode(pgm.val.val)
    else:
        raise ValueError('ICFP Program structure not recognized')


def decode(string: str) -> Program:
    """Serialize a program to the ICFP encoding"""
    return Program(String(strings.decode(string)))


def human_readable(pgm: Program) -> str:
    if pgm.val and isinstance(pgm.val, String):
        return pgm.val.val
    else:
        raise ValueError('ICFP Program structure not recognized')
