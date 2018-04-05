import io
import re

from wurlitzer import pipes

from opal.codegen import CodeGenerator
from opal.evaluator import OpalEvaluator


def get_string_name(string):
    return CodeGenerator.get_string_name(string)


class TestMath:
    def test_works_when_adding_integers(self):
        for expr in ['3 - 4', '3 + 4', '3 * 4', '3 / 4']:
            ev = OpalEvaluator()
            ev.evaluate(expr)

    def test_works_when_adding_float(self):
        for expr in ['3.1 - 4.3', '3.3 + 4.4', '23.1 * 4.2', '3.22 / 2.4']:
            ev = OpalEvaluator()
            ev.evaluate(expr)


class TestParser:
    def test_works_for_multi_line(self):
        expr = """
        3 + 4 * 6 + (4 / 2)
        """
        ev = OpalEvaluator()
        ev.evaluate(expr)

    def test_works_for_strings(self):
        opal_string = 'something something complete..'

        expr = f"""'{opal_string}'
        """
        ev = OpalEvaluator()
        ev.evaluate(expr)

        global_str_constant = r'@"str_[0-9a-fA-F]+" = private unnamed_addr constant \[31 x i8\] c"%s\\00"' % opal_string

        str(ev.codegen).should.match(global_str_constant)


class TestBuiltins:
    def test_includes_malloc(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare i8* @"malloc"(i32 %".1")')

    def test_includes_free_function(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare void @"free"(i8* %".1")')

    def test_includes_puts_function(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare i32 @"puts"(i8* %".1")')

    def test_includes_int_to_string_function(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare i8* @"int_to_string"(i32 %".1", i8* %".2", i32 %".3")')

    def test_includes_printf(self):
        ev = OpalEvaluator()
        str(ev.codegen).should.contain('declare i32 @"printf"(i8* %".1", ...)')


class TestExternal:
    def test_includes_int_to_c_function(self):
        ev = OpalEvaluator()
        ev.evaluate('1 / 1', run=False)
        # noinspection PyStatementEffect
        ev.llvm_mod.get_function('int_to_string').should.be.truthy


class TestPrinting:
    def test_works_for_strings(self):
        something_complete = f"""printing string"""
        expr = f"""print('%s')
        """ % something_complete

        ev = OpalEvaluator()
        ev.evaluate(expr)

        global_str_constant = \
            fr'@"str_[0-9a-fA-F]+" = private unnamed_addr constant \[16 x i8\] c"{something_complete}\\00"'

        str(ev.codegen).should.match(global_str_constant)
        str(ev.codegen).should.contain('%".3" = call i32 @"puts"(i8* %".2")')

    def test_works_for_multiple_strings(self):
        str1 = 'something special'
        str2 = 'something different'

        expr = f"""print('%s')
        print('%s')
        """ % (str1, str2)
        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain(str1)
        out.should.contain(str2)

    def test_twice_just_creates_one_constant(self):
        str1 = f"same thing printed twice"

        expr = f"""
        print('{str1}')
        print('{str1}')
        """
        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('same thing printed twice')

        const_string_declaration_regex = r'(@"str_[0-9a-fA-F]+" =)'
        re.findall(const_string_declaration_regex, str(ev.codegen), flags=re.MULTILINE).should.have.length_of(1)

    def test_works_for_integers(self):
        expr = f"print(432234)"

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('432234')

    def test_works_for_floats(self):
        expr = f"print(432.108)"

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('432.108')

    def test_works_for_arithmetics(self):
        expr = f"print(1000 / 10 - 80 + 22)"

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('42')

    def test_works_for_arithmetics_with_parenthesis(self):
        expr = f"print(1000 / (10 - 80) + 22)"

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('8')

    def test_works_for_booleans(self):
        expr = f"print(true)"

        ev = OpalEvaluator()
        ev.evaluate(expr)

        codegen = str(ev.codegen)

        str(codegen).should.contain(CodeGenerator.get_string_name('true'))

    def test_works_for_both_booleans(self):
        expr = f"""
        print(true)
        print(false)
        """

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('true')
        out.should.contain('false')


class TestComparison:
    def test_should_be_work_for_greater_than(self):
        expr = f"""
        print(2 > 1)
        """

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('true')

    def test_should_be_work_for_less_than(self):
        expr = f"""
        print(2 < 1)
        """

        ev = OpalEvaluator()

        with pipes() as (out, _):
            ev.evaluate(expr)

        out = out.read()

        out.should.contain('false')


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


