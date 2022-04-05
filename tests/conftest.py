import pytest

from jsonast import Parser


@pytest.fixture(scope="session")
def parser():
    return Parser()
