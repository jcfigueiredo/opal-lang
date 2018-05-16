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
        repres.should.contain('def_ name init params param name val block')

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
        repres.should.contain('def_ name init params param name val block boolean true')

    def test_supports_c_types(self):
        expr = """
        class Integer
            def init(val::Cint32)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name init params param name val ctype Cint32 block boolean true')

    def test_supports_types(self):
        expr = """
        class Integer
            def init(val::Integer)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ name init params param name val Integer block boolean true')


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
        prog.dump().should.contain('(class Integer(Block\n  (init(val) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_multiple_args(self):
        expr = """
        class Integer
            def init(val, other)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (init(val,other) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_no_args(self):
        expr = """
        class Integer
            def init()
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (init() (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_nc_typed_args(self):
        expr = """
        class Integer
            def init(val::Cint32)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (init(val::Cint32) (Block\n  (Boolean true)))))')


class TestTypeConstructorExecution:
    def test_generates_a_function(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def init()
            end
        end
        
        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::init"(%"Integer"* %".1")')

    def test_accepts_parameters(self, evaluator):
        expr = f"""
        class Object
        end

        class Integer
            def init(a, b)
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
            def init(val::Cint32)
            end
        end

        """

        evaluator.evaluate(expr, run=True)
        code = str(evaluator.codegen)

        code.should.contain('define void @"Integer::init"(%"Integer"* %".1", i32 %".2")')
