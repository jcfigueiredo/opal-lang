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

    def eval(self, expr):
        prog = self.get_parser().parse(expr)
        res = self.parsed_representation(prog)
        return res

    def test_handles_integers(self):
        expr = "1"

        res = self.eval(expr)

        res.should.equal('program block instruction int 1')

    def test_handles_floats(self):
        expr = "1.2"

        res = self.eval(expr)

        res.should.equal('program block instruction float 1.2')

    def test_handles_strings(self):
        expr = "'andrea'"

        res = self.eval(expr)
        res.should.equal('program block instruction string \'andrea\'')

    def test_handles_booleans_true(self):
        expr = "true"

        res = self.eval(expr)
        res.should.equal('program block instruction boolean true')

    def test_handles_booleans_false(self):
        expr = "false"

        res = self.eval(expr)
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

        res = self.eval(expr)

        res.should.equal('program block instruction add int 9 int 4')

    def test_adds_float(self):
        expr = "22.3 + 5.67"

        res = self.eval(expr)

        res.should.equal('program block instruction add float 22.3 float 5.67')

    def test_print_string(self):
        expr = "print('hi ho')"

        res = self.eval(expr)

        res.should.equal('program block instruction print string \'hi ho\'')

    def test_print_integer(self):
        expr = "print(1)"

        res = self.eval(expr)

        res.should.equal('program block instruction print int 1')

    def test_print_float(self):
        expr = "print(1.2)"

        res = self.eval(expr)

        res.should.equal('program block instruction print float 1.2')

    def test_print_expressions(self):
        expr = "print(1 + 2 * 3)"

        res = self.eval(expr)

        res.should.equal('program block instruction print add int 1 mul int 2 int 3')

    def test_sum_larger_than_nine(self):
        expr = """
        240 / 24
        """

        res = self.eval(expr)

        res.should.equal('program block instruction div int 240 int 24')

    def test_multiline_expression(self):
        expr = """
        240 / 24
        240 + 24
        """

        res = self.eval(expr)

        res.should.contain('instruction div int 240 int 24')
        res.should.contain('instruction add int 240 int 24')

    def test_compares_greater_and_less(self):
        expr = """
        24123 > 24
        10 < 12
        12.3 > 24.23
        10.11 < 12.43
        """

        res = self.eval(expr)
        res.should.contain('instruction comp int 24123 > int 24')
        res.should.contain('instruction comp int 10 < int 12')

        res.should.contain('instruction comp float 12.3 > float 24.23')
        res.should.contain('instruction comp float 10.11 < float 12.43')

    def test_compares_greater_than_and_less_than(self):
        expr = """
        24123 >= 24
        10 <= 12
        12.3 >= 24.23
        10.11 <= 12.43
        """

        res = self.eval(expr)
        res.should.contain('instruction comp int 24123 >= int 24')
        res.should.contain('instruction comp int 10 <= int 12')

        res.should.contain('instruction comp float 12.3 >= float 24.23')
        res.should.contain('instruction comp float 10.11 <= float 12.43')

    def test_compares_equal(self):
        expr = """
        12 == 24
        23.4 == 5.67
        """

        res = self.eval(expr)
        res.should.contain('instruction comp int 12 == int 24')
        res.should.contain('instruction comp float 23.4 == float 5.67')

    def test_compares_unequal(self):
        expr = """
        12 != 24
        23.4 != 5.67
        """

        res = self.eval(expr)
        res.should.contain('instruction comp int 12 != int 24')
        res.should.contain('instruction comp float 23.4 != float 5.67')

    def test_assigns_variable_to_constant(self):
        expr = """
        alpha = 123
        beta = 23.45
        gamma = "a j g"
        """

        res = self.eval(expr)
        res.should.contain('instruction assign alpha int 123')
        res.should.contain('instruction assign beta float 23.45')
        res.should.contain('instruction assign gamma string "a j g"')

    def test_assigns_variable_to_expression(self):
        expr = """
        alpha = 1 + 4
        """

        res = self.eval(expr)
        res.should.contain('instruction assign alpha add int 1 int 4')

    def test_assigns_variable_to_variable(self):
        expr = """
        alpha = beta
        """

        res = self.eval(expr)
        res.should.contain('instruction assign alpha beta')
