import re

from opal.parser import get_parser


# from lark.tree import pydot__tree_to_png  # Just a neat utility function
# pydot__tree_to_png(self.get_parser().parse(expr), "opal-grammar.png")


def get_representation(expr):
    def parsed_representation(prog):
        res = prog.pretty()
        res = re.sub(r"\s+", ' ', res)
        return res[:-1]

    prog = get_parser().parse(expr)
    res = parsed_representation(prog)
    return res


class TestLarkParser:

    def test_handles_integers(self):
        expr = "1"

        res = get_representation(expr)

        res.should.equal('program block instruction int 1')

    def test_handles_floats(self):
        expr = "1.2"

        res = get_representation(expr)

        res.should.equal('program block instruction float 1.2')

    def test_handles_strings(self):
        expr = "'andrea'"

        res = get_representation(expr)
        res.should.equal('program block instruction string \'andrea\'')

    def test_multi_line(self):
        expr = """1 - 1
        2 * 3
        """

        # noinspection PyUnusedLocal
        res = get_representation(expr)

    def test_single_statement(self):
        expr = """
        10 * 100
        """

        # noinspection PyUnusedLocal
        res = get_representation(expr)

    def test_single_line(self):
        expr = """1 - 1"""

        # noinspection PyUnusedLocal
        res = get_representation(expr)

    def test_adds_int(self):
        expr = "9 + 4"

        res = get_representation(expr)

        res.should.equal('program block instruction add int 9 int 4')

    def test_adds_float(self):
        expr = "22.3 + 5.67"

        res = get_representation(expr)

        res.should.equal('program block instruction add float 22.3 float 5.67')

    def test_print_string(self):
        expr = "print('hi ho')"

        res = get_representation(expr)

        res.should.equal('program block instruction print string \'hi ho\'')

    def test_print_integer(self):
        expr = "print(1)"

        res = get_representation(expr)

        res.should.equal('program block instruction print int 1')

    def test_print_float(self):
        expr = "print(1.2)"

        res = get_representation(expr)

        res.should.equal('program block instruction print float 1.2')

    def test_print_expressions(self):
        expr = "print(1 + 2 * 3)"

        res = get_representation(expr)

        res.should.equal('program block instruction print add int 1 mul int 2 int 3')

    def test_sum_larger_than_nine(self):
        expr = """
        240 / 24
        """

        res = get_representation(expr)

        res.should.equal('program block instruction div int 240 int 24')

    def test_multiline_expression(self):
        expr = """
        240 / 24
        240 + 24
        """

        res = get_representation(expr)

        res.should.contain('instruction div int 240 int 24')
        res.should.contain('instruction add int 240 int 24')

    def test_compares_greater_and_less(self):
        expr = """
        24123 > 24
        10 < 12
        12.3 > 24.23
        10.11 < 12.43
        """

        res = get_representation(expr)
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

        res = get_representation(expr)
        res.should.contain('instruction comp int 24123 >= int 24')
        res.should.contain('instruction comp int 10 <= int 12')

        res.should.contain('instruction comp float 12.3 >= float 24.23')
        res.should.contain('instruction comp float 10.11 <= float 12.43')

    def test_compares_equal(self):
        expr = """
        12 == 24
        23.4 == 5.67
        """

        res = get_representation(expr)
        res.should.contain('instruction comp int 12 == int 24')
        res.should.contain('instruction comp float 23.4 == float 5.67')

    def test_compares_unequal(self):
        expr = """
        12 != 24
        23.4 != 5.67
        """

        res = get_representation(expr)
        res.should.contain('instruction comp int 12 != int 24')
        res.should.contain('instruction comp float 23.4 != float 5.67')

    def test_assigns_variable_to_constant(self):
        expr = """
        alpha = 123
        beta = 23.45
        gamma = "a j g"
        delta = true
        """

        res = get_representation(expr)
        res.should.contain('instruction assign name alpha int 123')
        res.should.contain('instruction assign name beta float 23.45')
        res.should.contain('instruction assign name gamma string "a j g"')
        res.should.contain('instruction assign name delta boolean true')

    def test_assigns_variable_to_expression(self):
        expr = """
        alpha = 1 + 4
        beta = 2 * 3 / 4 - 1
        delta =  2 * (3 / (4 - 1))
        """

        res = get_representation(expr)
        res.should.contain('instruction assign name alpha add int 1 int 4')
        res.should.contain('instruction assign name beta sub div mul int 2 int 3 int 4 int 1')
        res.should.contain('instruction assign name delta mul int 2 div int 3 sub int 4 int 1')

    def test_prints_variables(self):
        expr = """
        alpha = 1 + 4
        print(alpha)
        """

        res = get_representation(expr)
        res.should.contain('instruction assign name alpha add int 1 int 4')
        res.should.contain('instruction print name alpha')

    def test_prints_boolean_variables(self):
        expr = """
        delta = true
        print(delta)
        """

        res = get_representation(expr)
        res.should.contain('instruction assign name delta boolean true')
        res.should.contain('instruction print name delta')

    def test_assigns_variable_to_variable(self):
        expr = """
        alpha = beta
        """

        res = get_representation(expr)
        res.should.contain('instruction assign name alpha name beta')


class TestSpecialCases:
    def test_handles_true_when_true_its_only_statement(self):
        expr = "true"

        res = get_representation(expr)

        res.should.equal('program block instruction name true')

    def test_handles_false_when_true_its_only_statement(self):
        expr = "false"

        res = get_representation(expr)

        # from lark.tree import pydot__tree_to_png  # Just a neat utility function
        # pydot__tree_to_png(self.get_parser().parse(expr), "opal-grammar.png")

        res.should.equal('program block instruction name false')
