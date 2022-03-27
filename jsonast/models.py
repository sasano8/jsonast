class NodeBase(dict):
    @classmethod
    def type(cls):
        return cls.__name__.lower()

    @property
    def nodes(self):
        return self[self.type()]["nodes"]

    @property
    def attrs(self):
        return self[self.type()]

    @property
    def has_attrs(self):
        size = len(self.attrs)
        if size == 1 and "nodes" in self.attrs:
            return False
        elif size == 0:
            return False
        else:
            return True

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
    def __init__(self, nodes=None, **attrs):
        self[self.type()] = attrs
        attrs["nodes"] = nodes or []

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
    def __init__(self, value=None, **attrs):
        self[self.type()] = attrs
        attrs["nodes"] = [value]

    @property
    def value(self):
        nodes = self.nodes
        if len(nodes) == 1:
            return nodes[0]
        elif len(nodes) == 0:
            return None
        else:
            raise ValueError()

    def simplify(self):
        if self.has_attrs:
            return self
        else:
            if isinstance(self.value, dict):
                return self
            else:
                return self.value
