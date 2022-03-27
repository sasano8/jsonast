import copy
import json
from itertools import chain
from typing import Union

from .models import Bool, Dict, Float, Int, List, Node, Null, Str, Undefined, Value


def create_mapper(types: set) -> dict:
    mapper = {
        typ.__name__.lower(): typ
        for typ in chain([Value, Null, Dict, List, Str, Int, Float, Bool], types)
    }
    return mapper


class AnonymousMapper(dict):
    def __getitem__(self, k):
        try:
            return super().__getitem__(k)
        except KeyError:
            cls = type(k, (Node,), {})
            self[k] = cls
            return cls


class Parser:
    def __init__(self, mapping: dict = {}, start: str = None):
        if isinstance(start, str):
            start = start.lower()

        self.mapping = mapping
        self.start = start
        self.to_node = self._create_to_node(mapping, start)

    @classmethod
    def build(cls, types: set = set(), start: str = None, as_anonymous: bool = False):
        mapper = create_mapper(types)
        if as_anonymous:
            mapper = AnonymousMapper(mapper)
        return cls(mapper, start)

    def load_from_file(self, fp):
        with open(fp, mode="r") as f:
            return self.load(f)

    def load(self, fp: Union[str, bytes]):
        obj = json.load(fp)
        return self.parse(obj, deepcopy=False)

    def loads(self, s):
        obj = json.loads(s)
        return self.parse(obj, deepcopy=False)

    def parse(self, obj, deepcopy: bool = True):
        obj = copy.deepcopy(obj)

        node = self.to_node(obj)
        if self.start is not None:
            if node.type() != self.start:
                raise ValueError()

        return node

    def dump(self, obj: Node, ensure_ascii: bool = False):
        result = obj.simplify()
        return json.dump(result, ensure_ascii=ensure_ascii)  # type: ignore

    def dumps(self, obj: Node, ensure_ascii: bool = False):
        result = obj.simplify()
        return json.dumps(result, ensure_ascii=ensure_ascii)

    @staticmethod
    def _create_to_node(mapper, start: str = None):
        def to_node(obj) -> Union["Node", "Value"]:
            nonlocal mapper

            if not isinstance(obj, dict):
                cls = mapper["value"]
                return cls(value=obj)

            try:
                k, attrs = next(iter(obj.items()))
            except StopIteration:
                raise TypeError("must be key")
            except:
                raise TypeError("no key")

            selector = mapper[k]
            cls, nodes, value, new_attrs = selector._split(attrs)
            if isinstance(nodes, list):
                nodes = [to_node(x) for x in nodes]
            elif nodes is Undefined:
                ...
            else:
                raise TypeError()

            selector._is_valid(value)
            return cls(nodes=nodes, value=value, **new_attrs)

        return to_node
