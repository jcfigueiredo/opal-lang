import pytest

from tests.helpers import get_representation, parse


class TestConstructorSyntax:
    def test_is_supported_for_no_args(self):
        expr = """
        class Integer
            def :init()
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('ctor_ name init')

    def test_has_a_body(self):
        expr = """
        class Integer
            def :init(val)
                true
            end
        end

        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('ctor_ name init params param name val block boolean true')

    def test_supports_untyped_parameters(self):
        expr = """
        class Integer
            def :init(val)
            end
        end

        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('ctor_ name init params param name val')

    def test_supports_multiple_untyped_parameters(self):
        expr = """
        class Integer
            def :init(val, another)
            end
        end

        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('ctor_ name init params param name val , param name another')

    def test_supports_typed_parameters(self):
        expr = """
        class Integer
            def :init(val::Cint32)
            end
        end

        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('ctor_ name init params param name val Cint32')


class TestConstructorAST:
    def test_has_a_default_constructor_when_no_constructor_is_specified(self):
        expr = """
        class Integer
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init()')

    def test_has_a_representation_for_no_args(self):
        expr = """
        class Integer
            def :init()
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init()')

    def test_should_have_only_one_default_constructor(self):
        expr = """
        class Integer
            def :init()
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.be.equal('(Program\n  (Block\n  (class Integer(Block\n  (:init() (Block\n  ))))))')

    def test_has_a_representation_with_one_arg(self):
        expr = """
        class Integer
            def :init(val)
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init(val)')

    def test_has_a_representation_for_multiple_args(self):
        expr = """
        class Integer
            def :init(val, other)
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init(val,other)')

    def test_has_a_representation_for_typed_args(self):
        expr = """
        class Integer
            def :init(val::Cint32)
            end
        end
        """
        prog = parse(expr)

        prog.dump().should.contain('(class Integer(Block\n  (:init(val::Cint32)')


class TestConstructorExecution:
    def test_generates_a_function(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def :init()
            end

        end

        """

        evaluator.evaluate(expr, run=False)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::init"(%"Integer"* %".1")')

    def test_accepts_parameters(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def :init(a, b)
            end
        end

        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::init"(%"Integer"* %".1", %"Object" %".2", %"Object" %".3")')

    def test_accepts_typed_parameters(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def :init(val::Cint32)
            end
        end

        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::init"(%"Integer"* %".1", i32 %".2")')
