from opal.evaluator import OpalEvaluator


# noinspection PyPep8Naming


class TestEvaluator:
    def test_works_when_adding_integers(self):
        for expr in ['3 - 4', '3 + 4', '3 * 4', '3 / 4']:
            ev = OpalEvaluator()
            ev.evaluate(expr)

    def test_works_when_adding_float(self):
        for expr in ['3.1 - 4.3', '3.3 + 4.4', '23.1 * 4.2', '3.22 / 2.4']:
            ev = OpalEvaluator()
            ev.evaluate(expr)
