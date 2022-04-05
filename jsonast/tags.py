import json
from typing import TYPE_CHECKING
from xml.etree import ElementTree


class Undefined:
    ...


Undefined = Undefined()  # type: ignore

if TYPE_CHECKING:

    class AnonymousTag(ElementTree.Element):
        ...

    class RestrictTag(ElementTree.Element):
        ...


else:

    class AnonymousTag:
        @property
        def tag(self) -> str:
            return self._tag

        @tag.setter
        def tag(self, value):
            self._tag = value

    class RestrictTag:
        @property
        def tag(self) -> str:
            return self.__class__.__name__.lower()

        @tag.setter
        def tag(self, value):
            self._tag = value


class ElementBase(ElementTree.Element):
    def set(self, key, value):
        if not isinstance(value, str):
            raise TypeError()

        self.attrib[key] = value


class Node(ElementBase, RestrictTag):
    @property
    def value(self) -> str:
        raise NotImplementedError()


class Json(ElementBase, RestrictTag):
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

    def __len__(self):
        return 0

    def append(self, subelement):
        raise NotImplementedError()

    def extend(self, elements):
        if not elements:
            return

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


class Var(Json, RestrictTag):
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value is None:
            raise TypeError()

        if not isinstance(value, str):
            raise TypeError()

        if value is None:
            self._text = None
            self._value = None
        else:
            self._text = json.dumps(value, ensure_ascii=False)
            self._value = value
