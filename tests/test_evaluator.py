from opal.evaluator import OpalEvaluator
from opal.codegen import  llvm


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

        global_str_constant = r'@"str_\d+" = private unnamed_addr constant \[31 x i8\] c"%s\\00"' % opal_string
        str(ev.codegen).should.match(global_str_constant)

    def test_works_for_printing_strings(self):
        expr = f"""print('something something complete..')
        """
        print(expr)
        ev = OpalEvaluator()
        ev.evaluate(expr)

        global_str_constant = r'@"str_\d+" = private unnamed_addr constant \[31 x i8\] c"%s\\00"' % \
                              'something something complete..'
        str(ev.codegen).should.match(global_str_constant)
        str(ev.codegen).should.contain('%".3" = call i32 @"puts"(i8* %".2")')

