from ast import parse
import copy

import pytest

from jsonast import Parser
from jsonast.tags import Node, Json
import inspect


@pytest.fixture(scope="session")
def parser():
    return Parser(
        {
            "default": lambda tag, attr: Node(tag, attr),
            "json": Json,
        }
    )


@pytest.fixture(scope="session")
def anonymous_parser():
    return Parser.build(set(), as_anonymous=True)


def test_parser_mapping(parser: Parser):
    assert len(parser.mapping) == 2
    assert parser.mapping["default"]
    assert parser.mapping["json"] is Json

    assert parser.selector("default")
    assert parser.selector("json") is Json

    # assert len(anonymous_parser.mapping) == 8
    # assert anonymous_parser.mapping == {
    #     "value": Value,
    #     "dict": Dict,
    #     "list": List,
    #     "str": Str,
    #     "int": Int,
    #     "float": Float,
    #     "bool": Bool,
    #     "null": Null,
    # }


def assert_common(parser: Parser, obj, expect_cls, expect_val):
    if inspect.isclass(expect_cls) and issubclass(expect_cls, Exception):
        with pytest.raises(expect_cls):
            parser.parse(obj)
        return
    else:
        result = parser.parse(obj)

    assert isinstance(result, expect_cls)

    if inspect.isclass(expect_val) and issubclass(expect_val, Exception):
        with pytest.raises(expect_val):
            result.value
        return
    else:
        assert result.value == expect_val


@pytest.mark.parametrize(
    "obj, expect_cls, expect_val",
    [
        (None, Exception, ...),
        (0, Exception, ...),
        (0.1, Exception, ...),
        ("", Exception, ...),
        (True, Exception, ...),
        (False, Exception, ...),
        ([], Exception, ...),
        ({}, Exception, ...),
    ],
)
def test_parse_stmt(parser, obj, expect_cls, expect_val):
    assert_common(parser, obj, expect_cls, expect_val)


@pytest.mark.parametrize(
    "obj, expect_cls, expect_val",
    [
        ({"json": None}, Json, None),
        ({"json": 0}, Json, 0),
        ({"json": 0.1}, Json, 0.1),
        ({"json": ""}, Json, ""),
        ({"json": True}, Json, True),
        ({"json": False}, Json, False),
        ({"json": []}, Json, []),
        ({"json": {}}, Json, {}),
    ],
)
def test_parse_stmt2(parser, obj, expect_cls, expect_val):
    assert_common(parser, obj, expect_cls, expect_val)


@pytest.mark.parametrize(
    "obj, expect_cls, expect_val",
    [
        ({"default": None}, Exception, ...),
        ({"default": 0}, Exception, ...),
        ({"default": 0.1}, Exception, ...),
        ({"default": ""}, Exception, ...),
        ({"default": True}, Exception, ...),
        ({"default": False}, Exception, ...),
        ({"default": []}, Node, Exception),
        ({"default": {}}, Node, Exception),
    ],
)
def test_parse_stmt3(parser, obj, expect_cls, expect_val):
    assert_common(parser, obj, expect_cls, expect_val)


@pytest.mark.parametrize(
    "obj, expect, as_str",
    [
        ({"node": []}, {"node": {"nodes": []}}, "{'node': []}"),
        (
            {"node": [1]},
            {"node": {"nodes": [{"json": {"value": 1}}]}},
            "{'node': [1]}",
        ),
        (
            {"node": [{"node": [1]}]},
            {"node": {"nodes": [{"node": {"nodes": [{"json": {"value": 1}}]}}]}},
            "{'node': [{'node': [1]}]}",
        ),
    ],
)
def test_parse(parser: Parser, anonymous_parser: Parser, obj, expect, as_str):
    result1 = parser.parse(obj).to_dict()
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
