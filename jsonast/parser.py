from .parser_json import JsonParser
from .parser_xml import XmlParser
from .tags import Node, Json


def create_selector(mapping: dict):
    mapping = mapping.copy()
    if "default" not in mapping:
        mapping["default"] = lambda tag: Node(tag)

    default = mapping.get("default")

    def selector(tag: str):
        return mapping.get(tag.lower(), default)

    return selector


class JsonAstParser:
    def __init__(
        self,
        mapping: dict = {
            "json": Json,
            "default": lambda tag: Node(tag),
        },
    ):
        self.mapping = mapping
        self.selector = create_selector(mapping)
        self.parser_xml = XmlParser(mapping)
        self.parser_json = JsonParser(mapping)

    def parse_from_xml_string(self, xml: str):
        return self.parser_xml.parse_from_xml_string(xml)

    def parse(self, obj, deepcopy: bool = True):
        return self.parser_json.parse(obj, deepcopy=True)