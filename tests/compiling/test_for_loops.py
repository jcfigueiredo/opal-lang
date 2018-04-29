from wurlitzer import pipes

from tests.helpers import get_representation, parse


# noinspection PyMethodMayBeStatic
class TestForLoopSyntax:
    def test_is_supported(self):
        expr = """
        for item in list
            print(item)
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ var item var list')
        repres.should.contain('block print var item')

    def test_supports_break(self):
        expr = """
        for item in list
            break            
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ var item var list')
        repres.should.contain('block break')

    def test_supports_continue(self):
        expr = """
        for item in list
            continue            
        end
        """

        repres = get_representation(expr)
        repres.should.contain('for_ var item var list')
        repres.should.contain('block continue')
