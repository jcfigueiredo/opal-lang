from wurlitzer import pipes

from tests.helpers import get_representation, parse


# noinspection PyMethodMayBeStatic
class TestWhileLoopSyntax:
    def test_is_supported(self):
        expr = """
        while true
            print("yay")
        end
        """

        repres = get_representation(expr)
        repres.should.contain('while_ boolean true')
        repres.should.contain('block print string "yay"')

    def test_supports_break(self):
        expr = """
        while true
            break            
        end
        """

        repres = get_representation(expr)
        repres.should.contain('while_ boolean true')
        repres.should.contain('block break')

    def test_supports_continue(self):
        expr = """
        while true
            continue            
        end
        """

        repres = get_representation(expr)
        repres.should.contain('while_ boolean true')
        repres.should.contain('block continue')


class TestWhileLoopAST:
    def test_has_a_representation(self):
        string = "Jed Bartlet"
        expr = f"""
        while true
            print("{string}")
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(Program\n  (Block\n  While((Boolean true)) '
                                   f'(Block\n  (Print (String {string})))))')

    def test_has_representation_for_breaks(self):

        expr = """
        while true
            break
        end
        """
        prog = parse(expr)
        prog.dump().should.contain(f'(Program\n  (Block\n  While((Boolean true)) '
                                   f'(Block\n  Break)))')


class TestWhileLoopsExecution:
    def test_leaves_the_loop_when_test_ends(self, evaluator):
        expr = f"""
        a = true
        while a
            print('in')
            a = false
        end 
        print('out')
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('in')
        out.should.contain('out')

    def test_leaves_the_loop_when_reaches_break(self, evaluator):
        expr = f"""
        a = true
        while a
            print('in')
            break
            print('unreachable')
        end 
        
        print('out')
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('in')
        out.should_not.contain('unreachable')
        out.should.contain('out')

    def test_can_include_complex_blocks(self, evaluator):
        expr = f"""
        num = 0

        while num <= 5
            print(num)
            num = num + 1
        end 
        
        """

        with pipes() as (out, _):
            evaluator.evaluate(expr)

        out = out.read()

        out.should.contain('0\n1\n2\n3\n4\n5')
