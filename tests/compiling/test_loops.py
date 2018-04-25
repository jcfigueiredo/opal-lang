from tests.helpers import get_representation, parse


# noinspection PyMethodMayBeStatic
class TestLoopSyntax:
    def test_is_supported(self):
        expr = """
        while true
            print("yay")
        end
        """

        repres = get_representation(expr)
        repres.should.contain('while_ boolean true')
        repres.should.contain('block print string "yay"')


class TestLoopAST:
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
