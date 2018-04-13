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
