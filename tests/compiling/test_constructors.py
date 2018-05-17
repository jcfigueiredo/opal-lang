from tests.helpers import get_representation, parse


class TestTypeMethodSyntax:
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

    def test_supports_returning_types(self):
        expr = """
        class Integer
            def Cint32 do_it(val::Cint32)
                true
            end
        end
        
        """

        repres = get_representation(expr)
        repres.should.contain('class_ name Integer')
        repres.should.contain('def_ Cint32 name do_it params param name val Cint32 block boolean true')


class TestTypeMethodAST:
    def test_has_a_representation(self):
        expr = """
        class Integer
            def do_it(val)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it(val) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_multiple_args(self):
        expr = """
        class Integer
            def do_it(val, other)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it(val,other) (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_no_args(self):
        expr = """
        class Integer
            def do_it()
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it() (Block\n  (Boolean true)))))')

    def test_has_a_representation_for_nc_typed_args(self):
        expr = """
        class Integer
            def do_it(val::Cint32)
                true
            end
        end
        """
        prog = parse(expr)
        prog.dump().should.contain('(class Integer(Block\n  (do_it(val::Cint32) (Block\n  (Boolean true)))))')


class TestTypeMethodExecution:
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
