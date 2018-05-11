# noinspection PyMethodMayBeStatic
from opal.codegen import CodeGenerator
from opal.evaluator import OpalEvaluator
from tests.helpers import get_representation, parse


class TestTypeCreationSyntax:
    def test_is_supported_with_variables(self):
        expr = """
        class Object
        end
        """

        repres = get_representation(expr)
        repres.should.contain('program block class_ name Object block')


class TestTypeInheritanceSyntax:
    def test_is_supported_with_variables(self):
        expr = """
        class Integer < Object
        end
        """

        repres = get_representation(expr)
        repres.should.contain('program block inherits name Integer name Object block')


class TestTypeCreationAST:
    def test_has_a_representation(self):
        expr = """
        class Object
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(class Object(Block\n  ))')


class TestTypeCreationWithInheritanceAST:
    def test_has_a_representation(self):
        expr = """
        class Integer < Object 
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(class Integer(Block\n  ))')


class TestCreatingANewType:
    @classmethod
    def setup_class(cls):
        expr = f"""
        class Object
        end
        """
        evaluator = OpalEvaluator()
        evaluator.evaluate(expr, run=False)
        cls.code = str(evaluator.codegen)

    def test_has_the_right_struct(self):
        self.code.should.contain('%"Object" = type {}')

    def test_creates_the_vtable_type(self):
        self.code.should.contain('%"Object_vtable_type" = type {%"Object_vtable_type"*, i8*}')

    def test_sets_the_type_name(self):
        self.code.should.contain('private unnamed_addr constant [7 x i8] c"Object\\00"')

    def test_creates_the_vtable(self):
        class_name = CodeGenerator.get_string_name('Object')
        self.code.should.contain(
            f'@"Object_vtable" = private constant %"Object_vtable_type" {{%"Object_vtable_type"* null, '
            f'i8* getelementptr ([7 x i8], [7 x i8]* @"{class_name}", i32 0, i32 0)}}')
