from wurlitzer import pipes

from tests.helpers import get_representation, parse


# noinspection PyMethodMayBeStatic
class TestForLoopSyntax:
    def test_is_supported_with_variables(self):
        expr = """
        for item in list
            print(item)
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ name item var list')
        repres.should.contain('block print var item')

    def test_is_supported_with_list(self):
        expr = """
        for item in [1, 2, 3]
            print(item)
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ name item list int 1 int 2 int 3')
        repres.should.contain('block print var item')

    def test_is_supported(self):
        expr = """
        for item in list
            print(item)
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ name item var list')
        repres.should.contain('block print var item')

    def test_supports_break(self):
        expr = """
        for item in list
            break            
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ name item var list')
        repres.should.contain('block break')

    def test_supports_continue(self):
        expr = """
        for item in list
            continue            
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ name item var list')
        repres.should.contain('block continue')


class TestForLoopAST:
    def test_has_a_representation(self):
        expr = """
        for item in list
            print(item)
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(Program\n  (Block\n  For((Var item) in (VarValue list)) '
                                   f'(Block\n  (Print (VarValue item)))))')

    def test_has_a_representation_for_lists(self):
        expr = """
        for item in [1, 2, 3]
            print(item)
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(
            f'(Program\n  (Block\n  For((Var item) in [(Integer 1), (Integer 2), (Integer 3)]) '
            f'(Block\n  (Print (VarValue item)))))')

    def test_has_representation_for_breaks(self):
        expr = """
        for item in list
            break
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(Program\n  (Block\n  For((Var item) in (VarValue list)) '
                                   f'(Block\n  Break)))')

    def test_has_representation_for_continue(self):
        expr = """
        for item in list
            continue
        end
        """

        prog = parse(expr)
        prog.dump().should.contain(f'(Program\n  (Block\n  For((Var item) in (VarValue list)) '
                                   f'(Block\n  Continue)))')


class TestForLoopsExecution:
    def test_leaves_the_loop_when_test_ends(self, evaluator):
        expr = f"""
        a_list = [2, 4, 6]
        for item in a_list
            print(item)
        end
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('2\n4\n6')

    def test_leaves_the_loop_when_reaches_break(self, evaluator):
        expr = f"""
        a_list = [200, 600]
        for item in a_list
            print(item)
            break
            print('unreachable')
        end 

        print('out')
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('200')
        out.should_not.contain('600')
        out.should_not.contain('unreachable')
        out.should.contain('out')

    def test_skips_when_reaches_continue(self, evaluator):
        expr = f"""
        a_list = [1, 2, 3 ,4, 5]
        for item in a_list
            if item == 3
                print("skipped") 
                continue
                print("never here")
            end
            print(item)
        end 

        print("out")
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('1')
        out.should.contain('2')
        out.should.contain('skipped')
        out.should.contain('4')
        out.should.contain('5')
        out.should.contain('out')
        out.should_not.contain('never here')
