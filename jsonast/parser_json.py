import json

from jsonast.tags import Json, Node
from xml.etree.ElementTree import Element
import copy


class Undefined:  # type: ignore
    ...


Undefined = Undefined()  # type: ignore


class JsonParser:
    def __init__(
        self,
        mapping: dict = {
            "default": lambda tag, attr: Node(tag, attr),
            "json": Json,
        },
    ):
        mapping = mapping.copy()
        if "default" not in mapping:
            mapping["default"] = lambda tag, attr: Node(tag, attr)

        default = mapping.get("default")

        def selector(tag: str):
            return mapping.get(tag.lower(), default)

        self.mapping = mapping
        self.selector = selector

    def parse_from_json_string(self, text: str):
        obj = json.loads(text)
        return self.parse_from_dict(obj)

    def parse_from_dict(self, obj: dict):
        if not isinstance(obj, dict):
            raise TypeError()

        return self.parse_node(obj)

    def parse(self, obj, deepcopy: bool = True):
        if not isinstance(obj, dict):
            raise TypeError("Must be dict top level.")

        obj = copy.deepcopy(obj)
        return self.parse_node(obj)

    def parse_node(self, obj):
        if not isinstance(obj, dict):
            return self.create_element("json", obj)

        try:
            tag, attrs = next(iter(obj.items()))
        except StopIteration:
            raise TypeError("must be key")
        except:
            raise TypeError("no key")

        return self.create_element(tag, attrs)

    def create_element(self, tag, attrs):
        factory = self.selector(tag)
        obj: Element = factory(tag, {})

        if isinstance(obj, Json):
            obj.value = attrs
            return obj

        if not isinstance(obj, Node):
            raise TypeError()

        if isinstance(attrs, dict):
            nodes = attrs.pop("nodes", Undefined)
            value = attrs.pop("value", Undefined)

            if nodes is not Undefined:
                if not isinstance(nodes, list):
                    raise TypeError()

                obj.extend(self.parse_node(x) for x in nodes)

            if value is not Undefined:
                obj.value = value  # type: ignore

            obj.attrib = attrs
            return obj

        elif isinstance(attrs, list):
            nodes = attrs
            attrs = {}
            value = Undefined

            if nodes is not Undefined:
                if not isinstance(nodes, list):
                    raise TypeError()

            obj.extend(self.parse_node(x) for x in nodes)
            obj.attrib = attrs
            return obj

        else:
            obj.value = attrs  # type: ignore
            return obj