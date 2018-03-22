import re

from opal.codegen import CodeGenerator
from opal.evaluator import OpalEvaluator


def get_string_name(string):
    return CodeGenerator.get_string_name(string)


class TestEvaluator:

    def test_works_when_adding_integers(self):
        for expr in ['3 - 4', '3 + 4', '3 * 4', '3 / 4']:
            ev = OpalEvaluator()
            ev.evaluate(expr)

    def test_works_when_adding_float(self):
        for expr in ['3.1 - 4.3', '3.3 + 4.4', '23.1 * 4.2', '3.22 / 2.4']:
            ev = OpalEvaluator()
            ev.evaluate(expr)

    def test_works_for_multi_line(self):
        expr = """
        3 + 4 * 6 + (4 / 2)
        """
        ev = OpalEvaluator()
        ev.evaluate(expr)

    def test_adds_malloc_builtins(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare i8* @"malloc"(i32 %".1")')

    def test_adds_free_builtins(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare void @"free"(i8* %".1")')

    def test_adds_puts_builtins(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare i32 @"puts"(i8* %".1")')

    def test_works_for_strings(self):
        opal_string = 'something something complete..'

        expr = f"""'{opal_string}'
        """
        ev = OpalEvaluator()
        ev.evaluate(expr)

        global_str_constant = r'@"str_[0-9a-fA-F]+" = private unnamed_addr constant \[31 x i8\] c"%s\\00"' % opal_string

        str(ev.codegen).should.match(global_str_constant)

    def test_works_for_printing_strings(self):
        something_complete = f"""printing string"""
        expr = f"""print('%s')
        """ % something_complete

        ev = OpalEvaluator()
        ev.evaluate(expr)

        global_str_constant = \
            fr'@"str_[0-9a-fA-F]+" = private unnamed_addr constant \[16 x i8\] c"{something_complete}\\00"'

        str(ev.codegen).should.match(global_str_constant)
        str(ev.codegen).should.contain('%".3" = call i32 @"puts"(i8* %".2")')

    def test_works_for_printing_multiple_strings(self):
        str1 = f"something"
        str2 = f"something different"

        expr = f"""print('%s')
        print('%s')
        """ % (str1, str2)
        ev = OpalEvaluator()
        ev.evaluate(expr)

        str(ev.codegen).should.contain(CodeGenerator.get_string_name(str1))
        str(ev.codegen).should.contain(CodeGenerator.get_string_name(str2))

    def test_printing_same_string_twice_just_creates_one_constant(self):
        str1 = f"same thing printed twice"

        expr = f"""
        print('{str1}')
        print('{str1}')
        """
        ev = OpalEvaluator()
        ev.evaluate(expr)

        const_string_declaration_regex = r'(@"str_[0-9a-fA-F]+" =)'
        re.findall(const_string_declaration_regex, str(ev.codegen), flags=re.MULTILINE).should.have.length_of(1)


class TestRegression:
    def test_simple_division(self):
        """
        Wrong configuration on Lark lead to parser ambiguity errors
        """
        expr = """
        10 / 2
        """

        ev = OpalEvaluator()

        ev.evaluate(expr)
