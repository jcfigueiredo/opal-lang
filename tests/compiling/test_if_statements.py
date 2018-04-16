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
