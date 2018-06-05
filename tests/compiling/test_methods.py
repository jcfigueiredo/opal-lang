from wurlitzer import pipes

from opal.codegen import CodeGenerator
from tests.helpers import get_representation, parse


class TestMethodDeclarationSyntax:
    def test_is_supported(self):
        expr = """
        class Integer
            def do_it(val)
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name do_it params param name val block')

    def test_has_a_body(self):
        expr = """
        class Integer
            def do_it(val)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name do_it params param name val block boolean true')

    def test_supports_types(self):
        expr = """
        class Integer
            def do_it(val::Cint32)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name do_it params param name val Cint32 block boolean true')

    def test_supports_setting_return_type(self):
        expr = """
        class Integer
            def Cint32 do_it(val::Cint32)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('typed_def Cint32 name do_it params param name val Cint32 block boolean true')

    def test_supports_returns(self):
        expr = """
        class Integer
            def Cint32 do_it(val::Cint32)
                return 10
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('typed_def Cint32 name do_it params param name val Cint32 block ret_ int 10')


class TestMethodCallSyntax:
    def test_is_supported(self):
        expr = """
        class MyClass
            def say_42()
                return 42
            end
        end
        mc = MyClass()
        
        mc.say_42()
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name MyClass')
        repres.should.contain('def_ name say_42 block')
        repres.should.contain('ret_ int 42')
        repres.should.contain('assign name mc instance name MyClass')
        repres.should.contain('method_call name mc name say_42')

    def test_variable_assigning_is_supported(self):
        expr = """
        class MyClass
            def say_42()
                return 42
            end
        end
        mc = MyClass()
        
        forty_two = mc.say_42()
        """

        repres = get_representation(expr)

        repres.should.contain('method_call name mc name say_42')
        repres.should.contain('assign name forty_two method_call name mc name say_42')


class TestTypeMethodDeclarationAST:
    def test_has_a_representation(self):
        expr = """
        class Integer
            def do_it(val)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it(val) (Block\n  (Bool true)')

    def test_has_a_representation_for_multiple_args(self):
        expr = """
        class Integer
            def do_it(val, other)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it(val,other) (Block\n  (Bool true)')

    def test_has_a_representation_for_no_args(self):
        expr = """
        class Integer
            def do_it()
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it() (Block\n  (Bool true)')

    def test_has_a_representation_for_typed_args(self):
        expr = """
        class Integer
            def do_it(val::Cint32)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it(val::Cint32) (Block\n  (Bool true)')

    def test_has_a_representation_for_returning_type(self):
        expr = """
        class Integer
            def Cint32 do_it(val::Cint32)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (Cint32 do_it(val::Cint32) (Block\n  (Bool true)')

    def test_has_a_representation_for_returns(self):
        expr = """
        class Integer
            def Cint32 do_it(val::Cint32)
                return 15
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (Cint32 do_it(val::Cint32) (Block\n  '
                                   '(Return (Integer 15)')


class TestTypeMethodCallAST:
    def test_has_a_representation(self):
        expr = """
        class MyClass
            def say_42()
                return 42
            end
        end
        mc = MyClass()
        
        mc.say_42()
        """
        prog = parse(expr)
        prog.dump().should.contain('(= mc MyClass())\n(mc.say_42 )')

    def test_has_representation_for_parameters(self):
        expr = """
        class MyClass
            def say_42()
                return 42
            end
        end
        mc = MyClass()
        
        mc.say_42(1, "2")
        """
        prog = parse(expr)
        prog.dump().should.contain('(= mc MyClass())\n(mc.say_42 (Integer 1), (String 2))')

    def test_has_representation_for_assigning_to_variables(self):
        expr = """
        class MyClass
            def say_42()
                return 42
            end
        end
        mc = MyClass()
        
        forty_two = mc.say_42()
        """
        prog = parse(expr)
        prog.dump().should.contain('(= mc MyClass())\n(= forty_two (mc.say_42 ))')


class TestTypeMethodDeclaration:
    def test_generates_a_function(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def do_it()
            end
        end
        
        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::do_it"(%"Integer"* %".1")')

    def test_accepts_parameters(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def do_it(a, b)
            end
        end
        
        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::do_it"(%"Integer"* %".1", %"Object" %".2", %"Object" %".3")')

    def test_accepts_typed_parameters(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def do_it(val::Cint32)
            end
        end

        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::do_it"(%"Integer"* %".1", i32 %".2")')

    # noinspection SpellCheckingInspection
    def test_accepts_return_type(self, evaluator):
        cname = 'Integer'
        pcname = 'Object'

        expr = f"""
        class {pcname}
        end

        class {cname}
            def Cint32 do_it(val::Cint32)
                return 42
            end
        end

        """

        evaluator.evaluate(expr, run=True, print_ir=False)
        code = str(evaluator.codegen)

        code.should.contain('%"Integer" = type {%"Integer_vtable_type"*}')
        code.should.contain('%"Integer_vtable_type" = type {%"Object_vtable_type"*, i8*, i32 (%"Integer"*, i32)*, '
                            'void (%"Integer"*)*}')

        class_name_ptr = CodeGenerator.get_string_name(cname)

        code.should.contain(
            f'@"{cname}_vtable" = private constant %"{cname}_vtable_type" '
            f'{{%"{pcname}_vtable_type"* @"{pcname}_vtable", '
            f'i8* getelementptr ([8 x i8], [8 x i8]* @"{class_name_ptr}", i32 0, i32 0), '
            f'i32 (%"Integer"*, i32)* @"Integer::do_it", void (%"Integer"*)* @"Integer::init"}}')

        code.should.contain('define i32 @"Integer::do_it"(%"Integer"* %".1", i32 %".2")')
        code.should.contain('ret i32 42')


class TestTypeMethodExecution:
    def test_generates_a_function(self, evaluator):
        expr = f"""
        
        class Object
        end
        
        class MyClass
            def say_42()
                return 42
            end
        end
        mc = MyClass()
        
        forty_two = mc.say_42()
        
        print(forty_two)

        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('42')

