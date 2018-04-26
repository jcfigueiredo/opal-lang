from wurlitzer import pipes


class TestVariables:

    def test_should_not_store_twice(self, evaluator):
        expr = f"""
        a = true
        a = false
        """
        evaluator.evaluate(expr, run=False)

        str(evaluator.llvm_mod).should_not.contain('store i1 false, i1* %a.1')

    def test_can_be_reassigned(self, evaluator):
        expr = f"""
        a = true
        a = false
        print(a)
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('false')

