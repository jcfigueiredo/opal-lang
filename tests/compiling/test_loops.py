from tests.helpers import get_representation


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
