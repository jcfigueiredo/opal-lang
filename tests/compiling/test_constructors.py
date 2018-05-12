from opal.codegen import CodeGenerator
from opal.evaluator import OpalEvaluator
from resources.llvmex import CodegenError
from tests.helpers import get_representation, parse


class TestTypeConstructorSyntax:
    def test_is_supported(self):
        expr = """
        class Integer
            def init(val)
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name init params name val block')

    def test_has_a_body(self):
        expr = """
        class Integer
            def init(val)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name init params name val block boolean true')


class TestTypeConstructorAST:
    def test_has_a_representation(self):
        expr = """
        class Integer
            def init(val)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(class Integer(Block\n  (init(val) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_multiple_args(self):
        expr = """
        class Integer
            def init(val, other)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(class Integer(Block\n  (init(val,other) (Block\n  (Boolean true)))))')
