from opal.evaluator import OpalEvaluator


# noinspection PyPep8Naming


class TestEvaluator:
    def test_works_with_the_simplest_code(self):
        ev = OpalEvaluator()

        result = ev.execute('3.4 - 4.0')

        str(result).should.contain('%"subtmp" = add float 0x400b333340000000, 0x4010000000000000')

    def test_forces_machine_target_for_now(self):
        ev = OpalEvaluator()

        result = ev.execute('1 / 1')

        str(result).should.contain('"x86_64-apple-macosx10.12.0"')
