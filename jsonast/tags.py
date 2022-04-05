import json
from xml.etree import ElementTree


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

    # def simplify(self):
    #     if len(self.value["attrs"]) == 0:
    #         self.value.pop("attrs", None)

    #     if len(self.value["nodes"]) == 0:
    #         self.value.pop("nodes", None)


class ElementBase(ElementTree.Element):
    def set(self, key, value):
        if not isinstance(value, str):
            raise TypeError()

        self.attrib[key] = value

    def to_dict(self):
        tag = self.__class__.__name__.lower()
        obj = {
            "attrs": self.attrib.copy(),
            "nodes": [x.to_obj() for x in self],  # type: ignore
            # "value": self.value,  # type: ignore
        }

        if len(obj["attrs"]) == 0:
            obj.pop("attrs", None)

        if len(obj["nodes"]) == 0:
            obj.pop("nodes", None)

        return KeyValue({tag: obj})

    def to_obj(self):
        return self.to_dict()

    def to_xml(self, as_byte: bool = False):
        if as_byte:
            return ElementTree.tostring(self)
        else:
            return ElementTree.tostring(self).decode("utf8")


class Node(ElementBase):
    @property
    def value(self):
        return None

    def to_dict(self):
        dic = super().to_dict()
        dic.value.pop("value", None)
        return dic

    @property
    def value(self):
        raise NotImplementedError()


class Json(ElementBase):
    def __init__(self, tag, attrib={}, **extra):
        typ = attrib.pop("type", "")
        if len(attrib) or len(extra):
            raise TypeError(f"can't set attributes in json tag: {attrib}")

        if typ == "":
            attrib = {}
        else:
            attrib = {"type": typ}

        super().__init__(tag, attrib)
        self.text = None

    def to_dict(self):
        dic = super().to_dict()
        dic.value.pop("nodes", None)
        dic["value"] = self.value
        return dic

    def to_obj(self):
        if len(self.attrib) == 0:
            if isinstance(self.value, dict):
                return self.to_dict()
            else:
                return self.value
        else:
            return self.to_dict()

    def __len__(self):
        return 0

    def append(self, subelement):
        raise NotImplementedError()

    def extend(self, elements):
        raise NotImplementedError()

    def insert(self, index, subelement):
        raise NotImplementedError()

    def __setitem__(self, index, element):
        raise NotImplementedError()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            self._text = None
            self._value = None
        else:
            self._text = json.dumps(value, ensure_ascii=False)
            self._value = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if value is None:
            self._value = None
            self._text = None
        else:
            try:
                self._value = json.loads(value)
            except json.JSONDecodeError as e:
                raise Exception(f"{str(e)}: {value}")
            self._text = value

    def set(self, key, value):
        raise NotImplementedError()
