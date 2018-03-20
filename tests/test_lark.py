import os
import re

import pytest
from lark.lark import Lark
from lark.lexer import Token
from lark.tree import InlineTransformer

import opal
from opal.ast import Block, Program, Float, Integer, Add, Div, Mul, Sub, String


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

    def test_print_string(self):
        expr = "print('hi ho')"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction print string \'hi ho\'')

    def test_print_integer(self):
        expr = "print(1)"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction print int 1')

    def test_print_float(self):
        expr = "print(1.2)"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction print float 1.2')

    def test_print_expressions(self):
        expr = "print(1 + 2 * 3)"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction print add int 1 mul int 2 int 3')

