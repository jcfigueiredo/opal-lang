from wurlitzer import pipes


class TestLists:
    def test_starts(self, evaluator):
        expr = f"""
        [1, 2, 3]
        """

        evaluator.evaluate(expr, run=False)

        str(evaluator.llvm_mod).should.contain('call void @vector_init({ i32, i32, i32* }* %.2)')
        str(evaluator.llvm_mod).should.contain('call void @vector_append({ i32, i32, i32* }* %.2, i32 1)')
        str(evaluator.llvm_mod).should.contain('call void @vector_append({ i32, i32, i32* }* %.2, i32 2)')
        str(evaluator.llvm_mod).should.contain('call void @vector_append({ i32, i32, i32* }* %.2, i32 3)')

    def test_supports_access_by_index(self, evaluator):
        expr = f"""
        [1, 2, 3, 4, 5, 6, 7][4]
        """

        evaluator.evaluate(expr, run=False)

        str(evaluator.llvm_mod).should.contain(' call i32 @vector_get({ i32, i32, i32* }* %.2, i32 4)')

    def test_can_be_printed(self, evaluator):
        expr = f"""
        print([11, 22, 33][1])        
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('22')
