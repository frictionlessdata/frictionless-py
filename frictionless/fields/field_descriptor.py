from __future__ import annotations

import datetime
from typing import List, Literal, Optional, Union

from pydantic import Field as PydanticField, BaseModel

from .base_field_descriptor import BaseFieldDescriptor
from .field_constraints import (
    BaseConstraints,
    CollectionConstraints,
    JSONConstraints,
    StringConstraints,
    ValueConstraints,
)

from .boolean_descriptor import BooleanFieldDescriptor
from .date_descriptor import DateFieldDescriptor
from .datetime_descriptor import DatetimeFieldDescriptor
from .duration_descriptor import DurationFieldDescriptor
from .integer_descriptor import IntegerFieldDescriptor


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


class AnyFieldDescriptor(BaseFieldDescriptor):
    """The field contains values of a unspecified or mixed type."""

    type: Literal["any"] = "any"
    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[str]] = None


IGeojsonFormat = Literal[
    "default",
    "topojson",
]


class GeoJSONFieldDescriptor(BaseFieldDescriptor):
    """The field contains a JSON object according to GeoJSON or TopoJSON spec."""

    type: Literal["geojson"] = "geojson"
    format: Optional[IGeojsonFormat] = None
    constraints: Optional[BaseConstraints[str]] = None


class GeoPointFieldDescriptor(BaseFieldDescriptor):
    """The field contains data describing a geographic point."""

    type: Literal["geopoint"] = "geopoint"
    format: Optional[IGeojsonFormat] = None
    constraints: Optional[BaseConstraints[str]] = None


class CategoryDict(BaseModel):
    """Category dictionary for field categories."""
    value: str
    label: Optional[str] = None


ICategories = Union[
    List[str],
    List[CategoryDict],
]
"""Categories type used by IntegerFieldDescriptor and StringFieldDescriptor"""


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


class NumberFieldDescriptor(BaseFieldDescriptor):
    """The field contains numbers of any kind including decimals."""

    type: Literal["number"] = "number"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[float]] = None

    decimal_char: Optional[str] = PydanticField(default=None, alias="decimalChar")
    """
    String whose value is used to represent a decimal point for number fields
    """

    group_char: Optional[str] = PydanticField(default=None, alias="groupChar")
    """
    String whose value is used to group digits for integer/number fields
    """

    bare_number: Optional[bool] = PydanticField(default=None, alias="bareNumber")
    """
    If false leading and trailing non numbers will be removed for integer/number fields
    """


class ObjectFieldDescriptor(BaseFieldDescriptor):
    """The field contains a valid JSON object."""

    type: Literal["object"] = "object"
    format: Optional[Literal["default"]] = None
    constraints: Optional[JSONConstraints] = None


IStringFormat = Literal[
    "binary",
    "default",
    "email",
    "uri",
    "uuid",
    # Unofficial
    "wkt",
]


class StringFieldDescriptor(BaseFieldDescriptor):
    """The field contains strings, that is, sequences of characters."""

    type: Literal["string"] = "string"
    format: Optional[IStringFormat] = None
    constraints: StringConstraints = PydanticField(default_factory=StringConstraints)

    categories: Optional[ICategories] = None
    """
    Property to restrict the field to a finite set of possible values
    """

    categoriesOrdered: Optional[bool] = None
    """
    When categoriesOrdered is true, implementations SHOULD regard the order of
    appearance of the values in the categories property as their natural order.
    """


class TimeFieldDescriptor(BaseFieldDescriptor):
    """The field contains a time without a date."""

    type: Literal["time"] = "time"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[datetime.time]] = None


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
