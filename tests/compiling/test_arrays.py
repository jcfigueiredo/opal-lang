from wurlitzer import pipes


class TestArrays:
    def test_starts(self, evaluator):

        expr = f"""
        [1, 2, 3]
        """

        evaluator.evaluate(expr, run=False)

        str(evaluator.llvm_mod).should.contain('call void @vector_init({ i32, i32, i32* }* %.2)')
        str(evaluator.llvm_mod).should.contain('call void @vector_append({ i32, i32, i32* }* %.2, i32 1)')
        str(evaluator.llvm_mod).should.contain('call void @vector_append({ i32, i32, i32* }* %.2, i32 2)')
        str(evaluator.llvm_mod).should.contain('call void @vector_append({ i32, i32, i32* }* %.2, i32 3)')
