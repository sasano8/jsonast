from typing import Union

from .tags import Json, Node, Undefined


class KeyValue(dict):
    @property
    def key(self):
        k, v = self.item
        return k

    @property
    def value(self):
        k, v = self.item
        return v

    @property
    def item(self):
        return next(iter(self.items()))


def to_obj(element: Union[Node, Json]):
    tag, attrs, nodes, value = normalize(element)
    nodes = [simplify(x) for x in nodes]
    obj = _to_dict(tag, attrs, nodes, value)
    result = _simplify(obj)


def normalize(element: Union[Node, Json]):
    tag = element.tag
    attrs = element.attrib.copy()
    nodes = element
    if isinstance(element, Json):
        value = element.value
    else:
        value = Undefined

    return tag, attrs, nodes, value


def _to_dict(tag, attrs, nodes, value):
    obj = {
        "attrs": attrs,
        "nodes": nodes,
        "value": value,
    }

    if len(attrs) == 0:
        obj.pop("attrs")

    if len(nodes) == 0:
        obj.pop("nodes")

    if value is Undefined:
        obj.pop("value")

    return KeyValue({tag: obj})


def to_dict(element: Union[Node, Json], func):
    tag, attrs, nodes, value = normalize(element)
    if func is not None:
        nodes = [func(x) for x in nodes]
    else:
        nodes = list(nodes)

    return _to_dict(tag, attrs, nodes, value)


def simplify(element: Union[Node, Json], is_root: bool = False):
    obj = to_dict(element, simplify)
    return _simplify(obj, is_root)


def _simplify(obj: KeyValue, is_root: bool = False):
    val = obj.value
    if len(val) == 0:
        return []

    if "value" in val:
        if isinstance(val["value"], dict):
            return obj
        else:
            if obj.key == "json":
                if is_root:
                    return {obj.key: val["value"]}
                else:
                    return val["value"]
            else:
                return {obj.key: val["value"]}
    else:
        if "attrs" in val:
            return obj
        else:
            if "nodes" in val:
                if obj.key == "node":
                    if is_root:
                        return {obj.key: val["nodes"]}
                    else:
                        return val["nodes"]
                else:
                    return {obj.key: val["nodes"]}
            else:
                if obj.key == "node":
                    if is_root:
                        return {obj.key: []}
                    else:
                        return []
                else:
                    return {obj.key: []}
