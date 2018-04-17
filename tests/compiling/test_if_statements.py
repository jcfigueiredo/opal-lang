from wurlitzer import pipes


class TestSimpleIfStatements:
    def test_handles_then_branch(self, evaluator):
        message = """Goes in."""

        expr = f"""
        if true then
            print("{message}")
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain(message)

    def test_handles_else_branch(self, evaluator):
        message = """Goes out."""

        expr = f"""
        if false then
            print("never gets here")
        else
            print("{message}")
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain(message)

    def test_works_with_variables(self, evaluator):
        expr = f"""
        exists = true
        if exists then
            print("oh yeah")
        else
            print("oh noh")
        end
        here = false
        if here then
            print("it's here")
        else
            print("it's there")
        end
        """
        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('oh yeah')
        out.should.contain('it\'s there')

    def test_works_with_comparison(self, evaluator):
        expr = f"""
        if 10 < 20 then
            print("20!")
        end

        if 1 > 2 then
            print("you're crazy")
        else
            print("one's ok")
        end
        """
        # evaluator.evaluate(expr)

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('20!')
        out.should.contain('one\'s ok')

    def test_works_with_expressions(self, evaluator):
        expr = f"""
        if 1 + 2 * 3 then
            print("seven")            
        end

        if 1 - 1 then
            print("weird")
        else
            print("zero")
        end

        if 1.3 + 3.7 then
            print("5.0")
        end

        if 2 > 1 then
            print("2 gt 1")
        end
                
        if 3 < 4 then
            print("3 lt 4")
        end
        
        if 3 == 3 then
            print("3 eq 3")
        end

        if 4 != 4 then
            print("4 neq 4")
        else
            print("4 eq 4")
        end
        
        if 2 + 3 == 5 then
            print("2 + 3 == 5")
        end
                
        if (2 + 3) * 4 - 2 == 9 * 2 then
            print("eighteen")
        end
                
        """

        # evaluator.evaluate(expr)
        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('seven')
        out.should.contain('zero')
        out.should.contain('5.0')
        out.should.contain('2 gt 1')
        out.should.contain('3 lt 4')
        out.should.contain('3 eq 3')
        out.should.contain('4 eq 4')
        out.should.contain('2 + 3 == 5')
        out.should.contain('eighteen')