import os
import re

import pytest
from lark.lark import Lark
from lark.lexer import Token
from lark.tree import InlineTransformer

import opal
from opal.ast import Block, Program, Float, Integer, Add, Div, Mul, Sub, String


# noinspection PyMethodMayBeStatic
class ASTVisitor(InlineTransformer):
    def program(self, body):
        if isinstance(body, Block):
            program = Program(body)
        else:
            program = Program(Block([body]))

        return program

    def block(self, *args):
        return Block([arg for arg in args if arg])

    # noinspection PyUnusedLocal
    def instruction(self, a, b=None):
        if isinstance(a, Token):
            return None
        return a

    def number(self, number):
        return number

    def add(self, lhs, rhs):
        return Add(lhs, rhs)

    def sub(self, lhs, rhs):
        return Sub(lhs, rhs)

    def mul(self, lhs, rhs):
        return Mul(lhs, rhs)

    def div(self, lhs, rhs):
        return Div(lhs, rhs)

    def int(self, const):
        return Integer(const.value)

    def float(self, const):
        return Float(const.value)

    def string(self, const):
        return String(const.value[1:][:-1])

    def term(self, nl):
        # newlines hanler
        return None


# from lark.tree import pydot__tree_to_png  # Just a neat utility function
# pydot__tree_to_png(res, "opal-grammar.png")


class TestLarkParser:
    def get_parser(self):
        opal_path = os.path.dirname(opal.__file__)
        grammar_file_path = os.path.join(opal_path, 'grammars', 'opal.g')

        with open(grammar_file_path, 'r') as f:
            parser = Lark(f.read(), debug=True, start='program', ambiguity='resolve')
        return parser

    @staticmethod
    def parsed_representation(prog):
        res = prog.pretty()
        res = re.sub(r"\s+", ' ', res)
        return res[:-1]

    def test_handles_integers(self):
        expr = "1"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction int 1')

    def test_handles_floats(self):
        expr = "1.2"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction float 1.2')

    def test_handles_strings(self):
        expr = "'andrea'"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)
        res.should.equal('program block instruction string \'andrea\'')

    def test_multi_line(self):
        expr = """1 - 1
        2 * 3
        """

        res = self.get_parser().parse(expr)
        # print(res.pretty())
        # print(GenerateAST().transform(res))
        # print(GenerateAST().transform(res).dump())

    def test_single_statement(self):
        expr = """
        10 * 100
        """

        res = self.get_parser().parse(expr)

        # print(res.pretty())
        # print(GenerateAST().transform(res))
        # print(GenerateAST().transform(res).dump())

    def test_single_line(self):
        expr = """1 - 1"""

        res = self.get_parser().parse(expr)

        # print(res.pretty())
        # print(GenerateAST().transform(res).dump())

    def test_adds_int(self):
        expr = "9 + 4"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction add int 9 int 4')

    def test_adds_float(self):
        expr = "22.3 + 5.67"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction add float 22.3 float 5.67')

