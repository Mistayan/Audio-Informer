from typing import Union

from dataclasses import dataclass

import dataclass_factory
from dataclass_factory import factory, schema_helpers


@dataclass
class Item:
    name: str
    type: str = "item"


@dataclass
class Group:
    name: str
    type: str = "group"


if __name__ == "__main__":
    Something = Union[Item, Group]  # Available types

    factory = factory.Factory(schemas={
        Item: schema_helpers.Schema(pre_parse=type_checker("item", field="type")),
        Group: schema_helpers.Schema(pre_parse=type_checker("group")),  # `type` is default name for checked field
    })
    assert factory.load({"name": "some name", "type": "group"}, Something) == Group("some name")

#
