class Undefined:
    ...


Undefined = Undefined()  # type: ignore


class Mapper(dict):
    @classmethod
    def _split(cls, attrs):
        raise NotImplementedError()

    @classmethod
    def _is_valid(cls, value):
        ...


class NodeBase(Mapper):
    @classmethod
    def _split(cls, attrs):

        if isinstance(attrs, list):
            nodes = attrs
            attrs = {}
        elif isinstance(attrs, dict):
            nodes = attrs.pop("nodes", [])
        else:
            raise TypeError()

        value = attrs.pop("value", Undefined)
        return cls, nodes, value, attrs

    def __init__(self, nodes=Undefined, value=Undefined, **attrs):
        raise NotImplementedError()

    @classmethod
    def type(cls):
        return cls.__name__.lower()

    @property
    def attrs(self):
        return self[self.type()]

    @property
    def nodes(self):
        raise NotImplementedError()

    @property
    def has_attrs(self) -> bool:
        raise NotImplementedError()

    def is_valid(self):
        if not (self.type() in self and len(self) == 1):
            raise TypeError()

        for err in self.validate():
            raise err

    def validate(self):
        yield from []

    def simplify(self):
        raise NotImplementedError()

    def __str__(self):
        return f"{self.simplify()}"


class Node(NodeBase):
    def __init__(self, nodes=None, *, value=Undefined, **attrs):
        self[self.type()] = attrs
        attrs["nodes"] = nodes or []

        if value is not Undefined:
            raise ValueError()

    @property
    def has_attrs(self):
        size = len(self.attrs)
        if size == 1 and "nodes" in self.attrs:
            return False
        elif size == 0:
            return False
        else:
            return True

    @property
    def nodes(self):
        return self[self.type()]["nodes"]

    def simplify(self):
        if self.has_attrs:
            return self
        else:
            obj = {self.type(): [self._simplify_node(x) for x in self.nodes]}
            return obj

    @staticmethod
    def _simplify_node(node):
        if isinstance(node, NodeBase):
            return node.simplify()
        elif isinstance(node, dict):
            raise TypeError()
        else:
            return node


class Value(NodeBase):
    @classmethod
    def _split(cls, attrs):
        if isinstance(attrs, list):
            value = attrs
            attrs = {}
        elif isinstance(attrs, dict):
            value = attrs.pop("value", None)
        else:
            raise TypeError()

        nodes = attrs.pop("nodes", Undefined)

        return cls, nodes, value, attrs

    def __init__(self, value=None, *, nodes=Undefined, **attrs):
        self[self.type()] = attrs

        if nodes is not Undefined:
            raise ValueError()

        attrs["value"] = self.normalize(value)

    def normalize(self, value):
        return value

    @property
    def has_attrs(self):
        size = len(self.attrs)
        if size == 1 and "value" in self.attrs:
            return False
        elif size == 0:
            return False
        else:
            return True

    @property
    def nodes(self):
        return [self.value]

    @property
    def value(self):
        return self[self.type()].get("value", None)

    def simplify(self):
        if self.has_attrs:
            return self
        else:
            v = self.value
            if isinstance(v, dict):
                return {"dict": v}
            else:
                return v


class ValueMapper(Mapper):
    @classmethod
    def _split(cls, attrs):
        return Value, Undefined, attrs, {}


class Null(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if value is not None:
            raise TypeError()


class Dict(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if not isinstance(value, dict):
            raise TypeError()


class List(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if not isinstance(value, list):
            raise TypeError()


class Str(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if not isinstance(value, str):
            raise TypeError()


class Int(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if not isinstance(value, int):
            raise TypeError()


class Float(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if not isinstance(value, (float, int)):
            raise TypeError()


class Bool(ValueMapper):
    @classmethod
    def _is_valid(cls, value):
        if not isinstance(value, bool):
            raise TypeError()
