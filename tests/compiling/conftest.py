import pytest

from opal.evaluator import OpalEvaluator


@pytest.fixture
def evaluator() -> OpalEvaluator:
    return OpalEvaluator()
