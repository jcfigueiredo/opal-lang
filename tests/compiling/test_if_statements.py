from wurlitzer import pipes


class TestIfStatements:

    def test_handles_then_branch(self, evaluator):
        message = """Goes in."""

        expr = f"""
        if true then
            print("{message}")
        end
        """

        # evaluator.evaluate(expr)

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain(message)

