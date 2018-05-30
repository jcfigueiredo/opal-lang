from tests.helpers import get_representation, parse


class TestInstanceSyntax:
    def test_is_supported_with_no_args(self):
        expr = """
        number = Integer()
        """

        repres = get_representation(expr)
        repres.should.contain('assign name number instance name Integer')

    def test_is_supported_with_args(self):
        expr = """
        number = Integer(1)
        items = Items(1, 2, 3)
        """

        repres = get_representation(expr)
        repres.should.contain('assign name number instance name Integer args arg int 1')
        repres.should.contain('assign name items instance name Items args arg int 1 , arg int 2 , arg int 3')


class TestInstanceAST:
    def test_has_a_representation_for_no_arg(self):
        expr = """
        number = Integer()
        """
        prog = parse(expr)
        prog.dump().should.contain('(= number Integer())')

    def test_has_a_representation_for_one_arg(self):
        expr = """
        number = Integer(1)
        """
        prog = parse(expr)
        prog.dump().should.contain('(= number Integer((Integer 1)))')

    def test_has_a_representation_for_multiple_arg(self):
        expr = """
        item = Foo(1, "bee", c)
        """
        prog = parse(expr)
        prog.dump().should.contain('(= item Foo((Integer 1), (String bee), (VarValue c)))')


class TestInstanceExecution:
    def test_alloca_and_calls_default_constructor(self, evaluator):
        expr = f"""
        class Object
        end

        class Foo
        end

        foo = Foo()

        """

        evaluator.evaluate(expr, run=True, print_ir=False)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Foo::init"(%"Foo"* %".1")')
        code.should.contain('%"foo" = alloca %"Foo"')
        code.should.contain('call void @"Foo::init"(%"Foo"* %"foo")')
