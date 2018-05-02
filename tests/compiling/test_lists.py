from wurlitzer import pipes

from tests.helpers import get_representation


class TestListSyntax:
    def test_assigns_lists(self):
        expr = """
        arr = [1, 2, 3]
        """

        repres = get_representation(expr)
        repres.should.contain('assign name arr list int 1 int 2 int 3')

    def test_with_multiple_items_is_supported(self):
        expr = "[1, 2, 3]"

        repres = get_representation(expr)

        repres.should.equal('program block list int 1 int 2 int 3')

    def test_with_one_item_is_supported(self):
        expr = "[77]"

        repres = get_representation(expr)

        repres.should.equal('program block list int 77')

    def test_empty_is_supported(self):
        expr = "[]"

        repres = get_representation(expr)

        repres.should.equal('program block list')


class TestListAccess:
    def test_works_for_explicit_lists(self):
        expr = "[10, 20, 30][2]"

        repres = get_representation(expr)

        repres.should.equal('program block list_access list int 10 int 20 int 30 index int 2')

    def test_works_for_variables(self):
        expr = "epta[22]"

        repres = get_representation(expr)

        repres.should.equal('program block list_access var epta index int 22')


class TestListExecution:
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

        str(evaluator.llvm_mod).should.contain('call i32 @vector_get({ i32, i32, i32* }* %.2, i32 4)')

    def test_items_can_be_printed(self, evaluator):
        expr = f"""
        print([11, 22, 33][1])        
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('22')

    def test_can_be_assigned_to_variables(self, evaluator):
        expr = f"""
        my_list = [100, 200, 234, 400, 8]
        print(my_list[2])        
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('234')
