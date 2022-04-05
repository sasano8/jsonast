import json
from typing import Literal, NamedTuple
from xml.etree import ElementTree
from xml.etree.ElementTree import Element

from jsonast import Parser


def test_xml():

    extra = {}
    select = Element("select", attrib={"aaa": "1<>'\""}, **extra)
    from_ = ElementTree.SubElement(select, "from")
    returning = ElementTree.SubElement(select, "returning")
    value = ElementTree.SubElement(returning, "value")
    value.text = "1<>'\""

    s = ElementTree.tostring(select, encoding="utf8", method="xml")
    print(s)


def test_xml_parser(parser: Parser):
    from jsonast.tags import Json, Node

    tree = parser.parse_from_xml_string(
        "<default></default>",
    )

    assert isinstance(tree, Node)
    assert parser.to_xml(tree) == "<default />"

    tree = parser.parse_from_xml_string(
        "<other></other>",
    )

    assert isinstance(tree, Node)
    assert parser.to_xml(tree) == "<other />"

    tree = parser.parse_from_xml_string("<json>1</json>")

    assert isinstance(tree, Json)
    assert tree.value == 1
    assert tree.text == "1"
    assert parser.to_xml(tree) == "<json>1</json>"


def test_load():
    xml = "<?xml version='1.0' encoding='utf8'?><select aaa=\"1&lt;&gt;'&quot;\"><from /><returning><value>1&lt;&gt;'\"</value></returning></select>"

    select = from_xml_string(xml)
    kv = to_key_value(select)

    assert kv == (
        "select",
        {
            "aaa": "1<>'\"",
            "text": None,
            "nodes": [
                ("from", {"text": None, "nodes": []}),
                (
                    "returning",
                    {
                        "text": None,
                        "nodes": [("value", {"text": "1<>'\"", "nodes": []})],
                    },
                ),
            ],
        },
    )

    assert [k for k, v in flatten(select)] == [
        "from",
        "value",
        "returning",
        "select",
    ]


def from_xml_file(path: str) -> Element:
    tree = ElementTree.parse(path)
    return tree.getroot()


def from_xml_string(xml: str) -> Element:
    return ElementTree.fromstring(xml)


def to_key_value(tree: Element):
    return tree.tag, {
        **tree.attrib,
        "text": tree.text,
        "nodes": [to_key_value(x) for x in tree],
    }


# breadth-first search?
# def events(tree: Element, func=lambda x: x):
#     nodes = [events(x, func) for x in tree]
#     result = {tree.tag: {**tree.attrib, "text": tree.text, "nodes": nodes}}
#     return func(result)


# depth-first search
# http://www2.toyo.ac.jp/~y-mizuno/Lang/appendix/tree_structure.pdf
# 先行順探索(preorder)
# 中間順探索(inorder) <= これを使うのがよさそう
# 後行順(postorder)
def events(tree: Element, func=lambda x: x):
    nodes = [events(x, func) for x in tree]
    result = (tree.tag, {**tree.attrib, "text": tree.text, "nodes": nodes})
    return func(result)


def flatten(tree, order: Literal["preorder", "inorder", "postorder"] = "inorder"):
    if order != "inorder":
        raise NotImplementedError()

    result = []

    def append(x):
        result.append(x)
        return x

    events(tree, append)
    return result
