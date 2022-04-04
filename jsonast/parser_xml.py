from jsonast.tags import Json, Statement
from xml.etree import ElementTree
from xml.etree.ElementTree import XMLParser as _XMLParser


class XmlParser:
    def __init__(
        self,
        mapping: dict = {
            "default": lambda tag, attr: Statement(tag, attr),
            "json": Json,
        },
    ):
        mapping = mapping.copy()
        if "default" not in mapping:
            mapping["default"] = lambda tag, attr: Statement(tag, attr)

        default = mapping.get("default")

        def selector(tag: str):
            return mapping.get(tag.lower(), default)

        self.selector = selector

    def create_element(self, tag: str, attrs):
        factory = self.selector(tag)
        return factory(tag, attrs)

    def parse_from_xml_string(self, xml: str):
        tb = ElementTree.TreeBuilder(element_factory=self.create_element)
        parser = _XMLParser(target=tb)
        return ElementTree.fromstring(
            xml,
            parser=parser,
        )
