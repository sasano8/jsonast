import copy

import pytest

from jsonast import Node, Parser, Value
from jsonast.models import Bool, Dict, Float, Int, List, Null, Str


@pytest.fixture(scope="session")
def parser():
    return Parser.build({Node})


@pytest.fixture(scope="session")
def anonymous_parser():
    return Parser.build(set(), as_anonymous=True)


def test_parser_mapping(parser: Parser, anonymous_parser: Parser):
    assert len(parser.mapping) == 9
    assert parser.mapping == {
        "node": Node,
        "value": Value,
        "dict": Dict,
        "list": List,
        "str": Str,
        "int": Int,
        "float": Float,
        "bool": Bool,
        "null": Null,
    }

    assert len(anonymous_parser.mapping) == 8
    assert anonymous_parser.mapping == {
        "value": Value,
        "dict": Dict,
        "list": List,
        "str": Str,
        "int": Int,
        "float": Float,
        "bool": Bool,
        "null": Null,
    }


def test_values(parser: Parser):
    parser.parse(None)
    parser.parse(0)
    parser.parse(0.0)
    parser.parse("")
    parser.parse(True)
    parser.parse(False)
    parser.parse([])
    with pytest.raises(Exception):
        parser.parse({})

    parser.parse({"null": None})
    parser.parse({"int": 0})
    parser.parse({"float": 0})
    parser.parse({"str": ""})
    parser.parse({"bool": True})
    parser.parse({"bool": False})
    parser.parse({"list": []})
    parser.parse({"dict": {}})

    with pytest.raises(Exception):
        parser.parse({"null": 0})
    with pytest.raises(Exception):
        parser.parse({"int": ""})
    with pytest.raises(Exception):
        parser.parse({"float": ""})
    with pytest.raises(Exception):
        parser.parse({"str": 1})
    with pytest.raises(Exception):
        parser.parse({"bool": 0})
    with pytest.raises(Exception):
        parser.parse({"bool": 0})
    with pytest.raises(Exception):
        parser.parse({"list": {}})
    with pytest.raises(Exception):
        parser.parse({"dict": []})


@pytest.mark.parametrize(
    "obj, expect, as_str",
    [
        ({"node": []}, {"node": {"nodes": []}}, "{'node': []}"),
        (
            {"node": [1]},
            {"node": {"nodes": [{"value": {"value": 1}}]}},
            "{'node': [1]}",
        ),
        (
            {"node": [{"node": [1]}]},
            {"node": {"nodes": [{"node": {"nodes": [{"value": {"value": 1}}]}}]}},
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

    assert parser.dumps(result1) == as_str.replace("'", '"')
    assert parser.dumps(result2) == as_str.replace("'", '"')
    assert parser.dumps(result3) == as_str.replace("'", '"')
    assert parser.dumps(result4) == as_str.replace("'", '"')
    assert anonymous_parser.dumps(result1) == as_str.replace("'", '"')
    assert anonymous_parser.dumps(result2) == as_str.replace("'", '"')
    assert anonymous_parser.dumps(result3) == as_str.replace("'", '"')
    assert anonymous_parser.dumps(result4) == as_str.replace("'", '"')

    assert str(result1) == as_str
    assert str(result2) == as_str
    assert str(result3) == as_str
    assert str(result4) == as_str
    assert str(result1.simplify()) == as_str
    assert str(result2.simplify()) == as_str
    assert str(result3.simplify()) == as_str
    assert str(result4.simplify()) == as_str
