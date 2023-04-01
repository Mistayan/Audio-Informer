from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional, TypeVar, Generic, Union

import dataclass_factory
from dataclass_factory import Schema, Factory
from dataclass_factory.schema_helpers import type_checker


@dataclass
class Author:
    name: str
    born_at: datetime


def parse_timestamp(data):
    print("parsing timestamp")
    return datetime.fromtimestamp(data, tz=timezone.utc)


T = TypeVar("T")
@dataclass
class FakeFoo(Generic[T]):
    value: T


@dataclass
class LinkedItem:
    value: Any
    next: Optional["LinkedItem"] = None

# --------- POLYMORPHISM --------- #
@dataclass
class Item:
    name: str
    type: str = "item"

@dataclass
class Group:
    name: str
    type: str = "group"
# --------- ------------ --------- #

def test_custom_parser_serializer():
    unixtime_schema = Schema(parser=parse_timestamp, serializer=datetime.timestamp)
    factory = Factory(schemas={datetime: unixtime_schema, })
    expected_author = Author("Petr", datetime(1970, 1, 2, 3, 4, 56, tzinfo=timezone.utc))
    data = {'born_at': 97496, 'name': 'Petr'}
    author = factory.load(data, Author)
    print(author, expected_author)
    assert author == expected_author

    serialized = factory.dump(author)
    assert data == serialized


def test_self_ref_type():
    data = {
        "value": 1,
        "next": {
            "value": 2
        }}
    factory = dataclass_factory.Factory()
    items = factory.load(data, LinkedItem)
    items = LinkedItem(1, LinkedItem(2))


def test_generi_class():
    factory = Factory(schemas={
        FakeFoo[str]: Schema(name_mapping={"value": "s"}),
        FakeFoo: Schema(name_mapping={"value": "i"}),
    })
    data = {"i": 42, "s": "Hello"}
    assert factory.load(data, FakeFoo[str]) == FakeFoo("Hello")  # found schema for concrete type
    assert factory.load(data, FakeFoo[int]) == FakeFoo(42)  # schema taken from generic version
    assert factory.dump(FakeFoo("hello"), FakeFoo[str]) == {"s": "hello"}  # concrete type is set explicitly
    assert factory.dump(FakeFoo("hello")) == {"i": "hello"}  # generic type is detected automatically
    print(factory.dump(FakeFoo("hello"), FakeFoo[str]))


def test_polymorphism():
    Something = Union[Item, Group]  # Available types

    factory = Factory(schemas={
        Item: Schema(pre_parse=type_checker("item", field="type")),
        Group: Schema(pre_parse=type_checker("group")),  # `type` is default name for checked field
    })
    assert factory.load({"name": "some name", "type": "group"}, Something) == Group("some name")


if __name__ == '__main__':
    test_self_ref_type()
    test_generi_class()
    test_custom_parser_serializer()
    test_polymorphism()