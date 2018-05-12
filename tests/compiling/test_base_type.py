# noinspection PyMethodMayBeStatic
from llvmlite.ir.context import Context

from opal.codegen import CodeGenerator
from opal.evaluator import OpalEvaluator
from resources.llvmex import CodegenError
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
        self.code.should.contain('%"Object" = type {%"Object_vtable_type"*}')

    def test_creates_the_vtable_type(self):
        self.code.should.contain('%"Object_vtable_type" = type {%"Object_vtable_type"*, i8*}')

    def test_sets_the_type_name(self):
        self.code.should.contain('private unnamed_addr constant [7 x i8] c"Object\\00"')

    def test_creates_the_vtable(self):
        class_name = CodeGenerator.get_string_name('Object')
        self.code.should.contain(
            f'@"Object_vtable" = private constant %"Object_vtable_type" {{%"Object_vtable_type"* null, '
            f'i8* getelementptr ([7 x i8], [7 x i8]* @"{class_name}", i32 0, i32 0)}}')


class TestClassWithNoParentDefined:
    def test_fails_when_declaring(self):
        expr = f"""
        class Integer < Bogus
        end
        """
        evaluator = OpalEvaluator()
        evaluator.evaluate.\
            when.called_with(expr, run=False).should.throw(CodegenError, 'Parent class Bogus not defined')


class TestCreatingANewTypeWithInheritance:
    class_name = 'Integer'
    parent_class_name = 'Object'

    @classmethod
    def setup_class(cls):
        expr = f"""
        class {cls.parent_class_name}
        end
        
        class {cls.class_name} < {cls.parent_class_name}
        end
        """
        evaluator = OpalEvaluator()
        evaluator.evaluate(expr, run=False)
        cls.code = str(evaluator.codegen)

    def test_creates_the_vtable_type_pointing_to_parent(self):
        self.code.should.contain('%"Integer_vtable_type" = type {%"Object_vtable_type"*, i8*}')

    def test_sets_the_type_name(self):
        self.code.should.contain('private unnamed_addr constant [8 x i8] c"Integer\\00"')

    def test_has_the_right_struct(self):
        self.code.should.contain('%"Integer" = type {%"Integer_vtable_type"*}')

    # noinspection SpellCheckingInspection
    def test_creates_the_vtable_pointing_to_parent(self):
        cname = self.class_name
        pcname = self.parent_class_name
        class_name_ptr = CodeGenerator.get_string_name(cname)
        self.code.should.contain(
            f'@"{cname}_vtable" = private constant %"{cname}_vtable_type" '
            f'{{%"{pcname}_vtable_type"* @"{pcname}_vtable", '
            f'i8* getelementptr ([8 x i8], [8 x i8]* @"{class_name_ptr}", i32 0, i32 0)}}')


class TestTypesWithExplicitInheritance:
    class_name = 'Integer'
    parent_class_name = 'Object'

    @classmethod
    def setup_class(cls):
        expr = f"""
        class {cls.parent_class_name}
        end
        
        class {cls.class_name}
        end
        
        """
        evaluator = OpalEvaluator()
        evaluator.evaluate(expr, run=False)
        cls.code = str(evaluator.codegen)

    def test_inherits_from_object_automatically(self):
        self.code.should.contain('%"Integer_vtable_type" = type {%"Object_vtable_type"*, i8*}')

    # noinspection SpellCheckingInspection
    def test_creates_the_vtable_pointing_to_object_vtable_automatically(self):
        cname = self.class_name
        pcname = self.parent_class_name
        class_name_ptr = CodeGenerator.get_string_name(cname)
        self.code.should.contain(
            f'@"{cname}_vtable" = private constant %"{cname}_vtable_type" '
            f'{{%"{pcname}_vtable_type"* @"{pcname}_vtable", '
            f'i8* getelementptr ([8 x i8], [8 x i8]* @"{class_name_ptr}", i32 0, i32 0)}}')
