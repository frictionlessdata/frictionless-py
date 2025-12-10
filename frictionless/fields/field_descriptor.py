from __future__ import annotations

from typing import Literal, Optional, Union

from pydantic import Field as PydanticField

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import (
    CollectionConstraints,
    JSONConstraints,
    ValueConstraints,
)

from .any_descriptor import AnyFieldDescriptor
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


class ArrayFieldDescriptor(BaseFieldDescriptor):
    """The field contains a valid JSON array."""

    type: Literal["array"] = "array"
    format: Optional[Literal["default"]] = None
    constraints: Optional[JSONConstraints] = None

    # TODO type is not accurate : array item are unnamed, not described etc
    # Using string annotation to avoid circular import
    array_item: Optional["FieldDescriptor"] = PydanticField(
        default=None, alias="arrayItem"
    )


IGeojsonFormat = Literal[
    "default",
    "topojson",
]



IItemType = Literal[
    "boolean",
    "date",
    "datetime",
    "integer",
    "number",
    "string",
    "time",
]


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


IStringFormat = Literal[
    "binary",
    "default",
    "email",
    "uri",
    "uuid",
    # Unofficial
    "wkt",
]


class YearFieldDescriptor(BaseFieldDescriptor):
    """The field contains a calendar year."""

    type: Literal["year"] = "year"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[int]] = None


class YearmonthFieldDescriptor(BaseFieldDescriptor):
    """The field contains a specific month of a specific year."""

    type: Literal["yearmonth"] = "yearmonth"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[str]] = None

FieldDescriptor = Union[
    AnyFieldDescriptor,
    ArrayFieldDescriptor,  # wip
    BooleanFieldDescriptor,  # v
    DateFieldDescriptor,  # v
    DatetimeFieldDescriptor,
    DurationFieldDescriptor,
    GeoJSONFieldDescriptor,
    GeoPointFieldDescriptor,
    IntegerFieldDescriptor,  # v
    ListFieldDescriptor,
    NumberFieldDescriptor,
    ObjectFieldDescriptor,
    StringFieldDescriptor,
    TimeFieldDescriptor,
    YearFieldDescriptor,
    YearmonthFieldDescriptor,
]
