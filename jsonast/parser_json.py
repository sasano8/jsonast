import copy
import json
from xml.etree.ElementTree import Element

from jsonml import Parser as BaseXMLParser

from jsonast.tags import Json, Node, Undefined


class JsonParser(BaseXMLParser):
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
            return self.create_node("json", obj)

        try:
            tag, attrs = next(iter(obj.items()))
        except StopIteration:
            raise TypeError("must be key")
        except:
            raise TypeError("no key")

        return self.create_node(tag, attrs)

    def create_node(self, tag, attrs):
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
