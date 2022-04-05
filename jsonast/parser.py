from typing import Callable, Type, Union
from xml.etree import ElementTree

from jsonml import BaseXMLParser
from jsonml import Parser as JsonMlParser
from jsonml import build_selector as _build_selector

from .parser_json import JsonParser
from .tags import AnonymousTag, Json
from .tags import Node as _Node


class Node(_Node, AnonymousTag):
    ...


def build_selector(
    mapping: dict = {
        "json": Json,
    },
    default: Union[str, None, Type[ElementTree.Element]] = Node,
) -> Callable[[str], Type[ElementTree.Element]]:
    return _build_selector(mapping=mapping, default=default)


default_selector = build_selector()


class JsonAstParser(BaseXMLParser):
    def __init__(self, selector: Union[dict, Callable] = default_selector):
        super().__init__(selector)

        self.parser_json = JsonParser(self.selector)
        self.parser_jsonml = JsonMlParser(self.selector)

    def parse_from_xml_string(self, xml: str):
        return self.parser_jsonml.parse_from_xml_string(xml)

    def parse_from_jsonml(self, obj: list, deepcopy: bool = True):
        return self.parser_jsonml.parse(obj, deepcopy=True)

    def parse_from_jsonast(self, obj: dict, deepcopy: bool = True):
        return self.parser_json.parse(obj, deepcopy=True)
