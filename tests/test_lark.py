import re

# from lark.tree import pydot__tree_to_png  # Just a neat utility function
# pydot__tree_to_png(res, "opal-grammar.png")
from opal.parser import parser


class TestLarkParser:
    @staticmethod
    def get_parser():
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

    def test_handles_booleans_true(self):
        expr = "true"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)
        res.should.equal('program block instruction boolean true')

    def test_handles_booleans_false(self):
        expr = "false"

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)
        res.should.equal('program block instruction boolean false')

    def test_multi_line(self):
        expr = """1 - 1
        2 * 3
        """

        # noinspection PyUnusedLocal
        res = self.get_parser().parse(expr)

    def test_single_statement(self):
        expr = """
        10 * 100
        """

        # noinspection PyUnusedLocal
        res = self.get_parser().parse(expr)

        # print(res.pretty())
        # print(GenerateAST().transform(res))
        # print(GenerateAST().transform(res).dump())

    def test_single_line(self):
        expr = """1 - 1"""

        # noinspection PyUnusedLocal
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

    def test_sum_larger_than_nine(self):
        expr = """
        240 / 24
        """

        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)

        res.should.equal('program block instruction div int 240 int 24')
