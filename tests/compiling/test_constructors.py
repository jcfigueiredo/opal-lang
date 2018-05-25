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
    def test_has_a_representation_for_no_args(self):
        expr = """
        class Integer
            def :init()
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init() (Block\n  (Boolean true)))))')

    def test_has_a_representation_with_one_arg(self):
        expr = """
        class Integer
            def :init(val)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init(val) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_multiple_args(self):
        expr = """
        class Integer
            def :init(val, other)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (:init(val,other) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_typed_args(self):
        expr = """
        class Integer
            def :init(val::Cint32)
                true
            end
        end
        """
        prog = parse(expr)

        prog.dump().should.contain('(class Integer(Block\n  (:init(val::Cint32) (Block\n  (Boolean true)))))')


# class TestConstructorExecution:
#     def test_generates_a_function(self, evaluator):
#         expr = f"""
#         class Object
#         end
#
#         class Integer
#             def :init()
#             end
#
#         end
#
#         """
#
#         evaluator.evaluate(expr, run=False)
#         code = str(evaluator.codegen)
#
#         code.should.contain('define void @"Integer:::init"(%"Integer"* %".1")')
#
#     def test_accepts_parameters(self, evaluator):
#         expr = f"""
#         class Object
#         end
#
#         class Integer
#             def do_it(a, b)
#             end
#         end
#
#         """
#
#         evaluator.evaluate(expr, run=True)
#         code = str(evaluator.codegen)
#
#         code.should.contain('define void @"Integer::do_it"(%"Integer"* %".1", %"Object" %".2", %"Object" %".3")')
#
#     def test_accepts_typed_parameters(self, evaluator):
#         expr = f"""
#         class Object
#         end
#
#         class Integer
#             def do_it(val::Cint32)
#             end
#         end
#
#         """
#
#         evaluator.evaluate(expr, run=True)
#         code = str(evaluator.codegen)
#
#         code.should.contain('define void @"Integer::do_it"(%"Integer"* %".1", i32 %".2")')
#
#     def test_accepts_return_type(self, evaluator):
#         expr = f"""
#         class Object
#         end
#
#         class Integer
#             def Cint32 do_it(val::Cint32)
#                 return 42
#             end
#         end
#
#         """
#
#         evaluator.evaluate(expr, run=True)
#         code = str(evaluator.codegen)
#
#         code.should.contain('define i32 @"Integer::do_it"(%"Integer"* %".1", i32 %".2")')
#         code.should.contain('ret i32 42')
