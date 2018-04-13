import pytest

from opal.evaluator import OpalEvaluator


@pytest.fixture
def evaluator():
    return OpalEvaluator()
