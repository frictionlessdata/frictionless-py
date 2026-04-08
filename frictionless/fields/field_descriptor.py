from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import Field as PydanticField

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import CollectionConstraints

from .any_descriptor import AnyFieldDescriptor
from .array_descriptor import ArrayFieldDescriptor
from .boolean_descriptor import BooleanFieldDescriptor
from .date_descriptor import DateFieldDescriptor
from .datetime_descriptor import DatetimeFieldDescriptor
from .duration_descriptor import DurationFieldDescriptor
from .geojson_descriptor import GeoJSONFieldDescriptor
from .geopoint_descriptor import GeoPointFieldDescriptor
from .integer_descriptor import IntegerFieldDescriptor
from .number_descriptor import NumberFieldDescriptor
from .object_descriptor import ObjectFieldDescriptor
from .string_descriptor import StringFieldDescriptor
from .time_descriptor import TimeFieldDescriptor
from .year_descriptor import YearFieldDescriptor
from .yearmonth_descriptor import YearmonthFieldDescriptor


IItemType = Literal[
    "boolean",
    "date",
    "datetime",
    "integer",
    "number",
    "string",
    "time",
]

# TODO: why is this not implemented?
class ListFieldDescriptor(BaseFieldDescriptor):
    """The field contains data that is an ordered
    one-level depth collection of primitive values with a fixed item type.
    """

    type: Literal["list"] = "list"
    format: Optional[Literal["default"]] = None
    constraints: CollectionConstraints = PydanticField(
        default_factory=CollectionConstraints
    )

    delimiter: Optional[str] = None
    """
    Specifies the character sequence which separates lexically represented list items.
    """

    item_type: Optional[IItemType] = PydanticField(default=None, alias="itemType")
    """
    Specifies the list item type in terms of existent Table Schema types.
    """


FieldDescriptorNoArrayOrList = Union[
    AnyFieldDescriptor,
    BooleanFieldDescriptor, 
    DateFieldDescriptor,
    DatetimeFieldDescriptor,
    DurationFieldDescriptor,
    GeoJSONFieldDescriptor,
    GeoPointFieldDescriptor,
    IntegerFieldDescriptor,
    NumberFieldDescriptor,
    ObjectFieldDescriptor,
    StringFieldDescriptor,
    TimeFieldDescriptor,
    YearFieldDescriptor,
    YearmonthFieldDescriptor,
]

# Recursive field descriptors (reference FieldDescriptor itself)
FieldDescriptor = Union[
    FieldDescriptorNoArrayOrList,
    ArrayFieldDescriptor,
    ListFieldDescriptor,
]
