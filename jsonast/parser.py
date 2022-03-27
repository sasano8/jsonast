import json
from typing import Union
import copy
from itertools import chain

from .models import Value, Node


def create_mapper(types: set) -> dict:
    mapper = {typ.__name__.lower(): typ for typ in chain([Value], types)}
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

    def parse(self, obj: dict, deepcopy: bool = True):
        obj = copy.deepcopy(obj)

        node = self.to_node(obj)
        if self.start is not None:
            if node.type() != self.start:
                raise ValueError()

        return node

    def dump(self):
        ...

    def dumps(self):
        ...

    @staticmethod
    def _create_to_node(mapper, start: str = None):
        def to_node(obj) -> Union["Node", "Value"]:
            nonlocal mapper

            if not isinstance(obj, dict):
                cls = mapper["value"]
                return cls(obj)

            try:
                k, attrs = next(iter(obj.items()))
            except:
                raise TypeError("no key")

            cls = mapper[k]

            if isinstance(attrs, list):
                nodes = attrs
                attrs = {}
            elif isinstance(attrs, dict):
                nodes = attrs.pop("nodes", [])
            else:
                raise TypeError()

            if issubclass(cls, Value):
                if not isinstance(nodes, list):
                    raise TypeError()

                if len(nodes) == 1:
                    return cls(nodes[0], **attrs)

                elif len(nodes) == 0:
                    return cls(None, **attrs)
                else:
                    raise ValueError()
            else:
                nodes = [to_node(x) for x in nodes]
                return cls(nodes, **attrs)

        return to_node
