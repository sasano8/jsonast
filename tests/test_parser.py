import pytest
import copy

from jsonast import Node, Parser, Value


@pytest.fixture(scope="session")
def parser():
    return Parser.build({Node})


@pytest.fixture(scope="session")
def anonymous_parser():
    return Parser.build(set(), as_anonymous=True)


def test_parser_mapping(parser: Parser, anonymous_parser: Parser):
    assert parser.mapping == {"node": Node, "value": Value}

    assert len(anonymous_parser.mapping) == 1
    assert anonymous_parser.mapping == {"value": Value}


@pytest.mark.parametrize(
    "obj, expect, as_str",
    [
        ({"node": []}, {"node": {"nodes": []}}, "{'node': []}"),
        (
            {"node": [1]},
            {"node": {"nodes": [{"value": {"nodes": [1]}}]}},
            "{'node': [1]}",
        ),
        (
            {"node": [{"node": [1]}]},
            {"node": {"nodes": [{"node": {"nodes": [{"value": {"nodes": [1]}}]}}]}},
            "{'node': [{'node': [1]}]}",
        ),
    ],
)
def test_parse(parser: Parser, anonymous_parser: Parser, obj, expect, as_str):
    result1 = parser.parse(obj)
    assert result1 == expect

    result2 = anonymous_parser.parse(obj)
    assert result1 == result2

    copied = copy.deepcopy(result1)

    result3 = parser.parse(result1)
    assert result3 == expect

    result4 = anonymous_parser.parse(result1)
    assert result3 == result4
    assert result1 == copied

    assert parser.parse(result1.simplify()) == expect
    assert parser.parse(result2.simplify()) == expect
    assert parser.parse(result3.simplify()) == expect
    assert parser.parse(result4.simplify()) == expect
    assert anonymous_parser.parse(result1.simplify()) == expect
    assert anonymous_parser.parse(result2.simplify()) == expect
    assert anonymous_parser.parse(result3.simplify()) == expect
    assert anonymous_parser.parse(result4.simplify()) == expect

    assert str(result1) == as_str
    assert str(result2) == as_str
    assert str(result3) == as_str
    assert str(result4) == as_str
    assert str(result1.simplify()) == as_str
    assert str(result2.simplify()) == as_str
    assert str(result3.simplify()) == as_str
    assert str(result4.simplify()) == as_str