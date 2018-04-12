import re

from opal.parser import get_parser


# from lark.tree import pydot__tree_to_png  # Just a neat utility function
# pydot__tree_to_png(self.get_parser().parse(expr), "opal-grammar.png")


def get_representation(expr):
    def parsed_representation(prog):
        repres = prog.pretty()
        repres = re.sub(r"\s+", ' ', repres)
        return repres[:-1]

    prog = get_parser().parse(f'{expr}\n')
    repres = parsed_representation(prog)
    return repres


class TestLarkParser:

    def test_handles_integers(self):
        expr = "1"

        repres = get_representation(expr)

        repres.should.equal('program block int 1')

    def test_handles_floats(self):
        expr = "1.2"

        repres = get_representation(expr)

        repres.should.equal('program block float 1.2')

    def test_handles_strings(self):
        expr = "'andrea'"

        repres = get_representation(expr)
        repres.should.equal('program block string \'andrea\'')

    def test_multi_line(self):
        expr = """1 - 1
        2 * 3
        """

        # noinspection PyUnusedLocal
        repres = get_representation(expr)

    def test_single_statement(self):
        expr = """
        10 * 100
        """

        # noinspection PyUnusedLocal
        repres = get_representation(expr)

    def test_single_line(self):
        expr = """1 - 1"""

        # noinspection PyUnusedLocal
        repres = get_representation(expr)

    def test_adds_int(self):
        expr = "9 + 4"

        repres = get_representation(expr)

        repres.should.equal('program block add int 9 int 4')

    def test_adds_float(self):
        expr = "22.3 + 5.67"

        repres = get_representation(expr)

        repres.should.equal('program block add float 22.3 float 5.67')

    def test_print_string(self):
        expr = "print('hi ho')"

        repres = get_representation(expr)

        repres.should.equal('program block print string \'hi ho\'')

    def test_print_integer(self):
        expr = "print(1)"

        repres = get_representation(expr)

        repres.should.equal('program block print int 1')

    def test_print_float(self):
        expr = "print(1.2)"

        repres = get_representation(expr)

        repres.should.equal('program block print float 1.2')

    def test_print_expressions(self):
        expr = "print(1 + 2 * 3)"

        repres = get_representation(expr)

        repres.should.equal('program block print add int 1 mul int 2 int 3')

    def test_sum_larger_than_nine(self):
        expr = """
        240 / 24
        """

        repres = get_representation(expr)

        repres.should.equal('program block div int 240 int 24')

    def test_multiline_expression(self):
        expr = """
        240 / 24
        240 + 24
        """

        repres = get_representation(expr)

        repres.should.contain('div int 240 int 24')
        repres.should.contain('add int 240 int 24')

    def test_compares_greater_and_less(self):
        expr = """
        24123 > 24
        10 < 12
        12.3 > 24.23
        10.11 < 12.43
        """

        repres = get_representation(expr)
        repres.should.contain('comp int 24123 > int 24')
        repres.should.contain('comp int 10 < int 12')

        repres.should.contain('comp float 12.3 > float 24.23')
        repres.should.contain('comp float 10.11 < float 12.43')

    def test_compares_greater_than_and_less_than(self):
        expr = """
        24123 >= 24
        10 <= 12
        12.3 >= 24.23
        10.11 <= 12.43
        """

        repres = get_representation(expr)
        repres.should.contain('comp int 24123 >= int 24')
        repres.should.contain('comp int 10 <= int 12')

        repres.should.contain('comp float 12.3 >= float 24.23')
        repres.should.contain('comp float 10.11 <= float 12.43')

    def test_compares_equal(self):
        expr = """
        12 == 24
        23.4 == 5.67
        """

        repres = get_representation(expr)
        repres.should.contain('comp int 12 == int 24')
        repres.should.contain('comp float 23.4 == float 5.67')

    def test_compares_unequal(self):
        expr = """
        12 != 24
        23.4 != 5.67
        """

        repres = get_representation(expr)
        repres.should.contain('comp int 12 != int 24')
        repres.should.contain('comp float 23.4 != float 5.67')

    def test_assigns_variable_to_constant(self):
        expr = """
        alpha = 123
        beta = 23.45
        gamma = "a j g"
        delta = true
        """

        repres = get_representation(expr)
        repres.should.contain('assign name alpha int 123')
        repres.should.contain('assign name beta float 23.45')
        repres.should.contain('assign name gamma string "a j g"')
        repres.should.contain('assign name delta boolean true')

    def test_assigns_variable_to_expression(self):
        expr = """
        alpha = 1 + 4
        beta = 2 * 3 / 4 - 1
        delta =  2 * (3 / (4 - 1))
        """

        repres = get_representation(expr)
        repres.should.contain('assign name alpha add int 1 int 4')
        repres.should.contain('assign name beta sub div mul int 2 int 3 int 4 int 1')
        repres.should.contain('assign name delta mul int 2 div int 3 sub int 4 int 1')

    def test_prints_variables(self):
        expr = """
        alpha = 1 + 4
        print(alpha)
        """

        repres = get_representation(expr)
        repres.should.contain('assign name alpha add int 1 int 4')
        repres.should.contain('print name alpha')

    def test_prints_boolean_variables(self):
        expr = """
        delta = true
        print(delta)
        """

        repres = get_representation(expr)
        repres.should.contain('assign name delta boolean true')
        repres.should.contain('print name delta')

    def test_assigns_variable_to_variable(self):
        expr = """
        alpha = beta
        """

        repres = get_representation(expr)
        repres.should.contain('assign name alpha name beta')


class TestConditionals:
    def test_works_for_booleans_with_no_else(self):
        expr = """
        if true then
            a = 1
        end
        print(a)
        """

        repres = get_representation(expr)
        repres.should.contain('if_ boolean true block ')
        repres.should.contain('assign name a int 1 ')
        repres.should.contain('print name a')

    def test_works_for_booleans_with_else(self):
        expr = """
        if true then
            a = 1
        else
            a = 2
        end
        """

        repres = get_representation(expr)
        repres.should.contain('if_ boolean true')
        repres.should.contain('block assign name a int 1 ')
        repres.should.contain('block assign name a int 2')
        '''
        program block if_ boolean true 
            block assign name a int 1 
            block assign name a int 2 
        '''

    def test_works_for_multiline_else(self):
        expr = """
        if true then
            a = 1
            b = 2.2
        else
            "amora"
            print(a)
        end

        1
        false
        """

        # parser = get_parser()
        #
        # prog = parser.parse(f'{expr}\n')
        #
        # print(prog.pretty())
        #
        repres = get_representation(expr)
        repres.should.contain('if_ boolean true block')
        repres.should.contain('assign name a int 1 ')
        repres.should.contain('assign name b float 2.2')
        repres.should.contain('block string "amora"')
        repres.should.contain('print name a')


class TestSpecialCases:
    def test_handles_true_when_true_its_only_statement(self):
        expr = "true"

        repres = get_representation(expr)

        repres.should.equal('program block boolean true')

    def test_handles_false_when_true_its_only_statement(self):
        expr = "false"

        repres = get_representation(expr)

        repres.should.equal('program block boolean false')
