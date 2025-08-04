"""field_descriptor.py provides pydantic Models for Field descriptors"""

from __future__ import annotations

import datetime
from typing import Any, Dict, List, Literal, Optional, Union

import pydantic
from typing_extensions import Self

from .. import settings
from .field_constraints import (
    BaseConstraints,
    CollectionConstraints,
    JSONConstraints,
    StringConstraints,
    ValueConstraints,
)


class BaseFieldDescriptor(pydantic.BaseModel):
    """Data model of a (unspecialised) field descriptor"""

    name: str
    """
    The field descriptor MUST contain a name property.
    """

    title: Optional[str] = None
    """
    A human readable label or title for the field
    """

    description: Optional[str] = None
    """
    A description for this field e.g. “The recipient of the funds”
    """

    missing_values: Optional[List[str]] = pydantic.Field(
        default=None, alias="missingValues"
    )
    """
    A list of field values to consider as null values
    """

    example: Optional[str] = None
    """
    An example of a value for the field.
    """

    @pydantic.model_validator(mode="before")
    @classmethod
    def compat(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        # Backward compatibility for field.format

        format_ = data.get("format")
        if format_:
            if format_.startswith("fmt:"):
                data["format"] = format_[4:]

        return data


class BooleanFieldDescriptor(BaseFieldDescriptor):
    """The field contains boolean (true/false) data."""

    type: Literal["boolean"] = "boolean"

    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[bool]] = None

    true_values: Optional[List[str]] = pydantic.Field(
        default=settings.DEFAULT_TRUE_VALUES,
        alias="trueValues",
        validation_alias=pydantic.AliasChoices("trueValues", "true_values"),
    )
    """
    Values to be interpreted as “true” for boolean fields
    """

    false_values: Optional[List[str]] = pydantic.Field(
        default=settings.DEFAULT_FALSE_VALUES,
        alias="falseValues",
        validation_alias=pydantic.AliasChoices("falseValues", "false_values"),
    )
    """
    Values to be interpreted as “false” for boolean fields
    """

    def read_value(self, cell: Any):
        if isinstance(cell, bool) and cell is True or cell is False:
            return cell

        if isinstance(cell, str):
            if self.true_values and cell in self.true_values:
                return True
            if self.false_values and cell in self.false_values:
                return False
            return None

    def write_value(self, cell: Any):
        if self.true_values and self.false_values:
            return self.true_values[0] if cell else self.false_values[0]
        return None

    @pydantic.model_validator(mode="after")
    def validate_example(self) -> Self:
        # If example is provided, check it's in true_values or false_values
        if self.example is not None:
            allowed_values = (self.true_values or []) + (self.false_values or [])
            if self.example not in allowed_values:
                raise ValueError(
                    f'example value "{self.example}" for field "{self.name}" is not valid'
                )

        return self


class ArrayFieldDescriptor(BaseFieldDescriptor):
    """The field contains a valid JSON array."""

    type: Literal["array"] = "array"
    format: Optional[Literal["default"]] = None
    constraints: Optional[JSONConstraints] = None

    # TODO type is not accurate : array item are unnamed, not described etc
    array_item: Optional[FieldDescriptor] = pydantic.Field(
        default=None, alias="arrayItem"
    )


class AnyFieldDescriptor(BaseFieldDescriptor):
    """The field contains values of a unspecified or mixed type."""

    type: Literal["any"] = "any"
    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[str]] = None


class DateFieldDescriptor(BaseFieldDescriptor):
    """he field contains a date without a time."""

    type: Literal["date"] = "date"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[str]] = None


class DatetimeFieldDescriptor(BaseFieldDescriptor):
    """The field contains a date with a time."""

    type: Literal["datetime"] = "datetime"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[datetime.datetime]] = None


class DurationFieldDescriptor(BaseFieldDescriptor):
    """The field contains a duration of time."""

    type: Literal["duration"] = "duration"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[str]] = None


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


class CategoryDict(pydantic.BaseModel):
    value: str
    label: Optional[str] = None


ICategories = Union[
    List[str],
    List[CategoryDict],
]


class IntegerFieldDescriptor(BaseFieldDescriptor):
    """The field contains integers - that is whole numbers."""

    type: Literal["integer"] = "integer"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[int]] = None

    categories: Optional[ICategories] = None
    """
    Property to restrict the field to a finite set of possible values
    """

    categories_ordered: Optional[bool] = pydantic.Field(
        default=None, alias="categoriesOrdered"
    )
    """
    When categoriesOrdered is true, implementations SHOULD regard the order of
    appearance of the values in the categories property as their natural order.
    """

    group_char: Optional[str] = pydantic.Field(default=None, alias="groupChar")
    """
    String whose value is used to group digits for integer/number fields
    """

    bare_number: Optional[bool] = pydantic.Field(default=None, alias="bareNumber")
    """
    If false leading and trailing non numbers will be removed for integer/number fields
    """


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
    constraints: CollectionConstraints = pydantic.Field(
        default_factory=CollectionConstraints
    )

    delimiter: Optional[str] = None
    """
    Specifies the character sequence which separates lexically represented list items.
    """

    item_type: Optional[IItemType] = pydantic.Field(default=None, alias="itemType")
    """
    Specifies the list item type in terms of existent Table Schema types.
    """


class NumberFieldDescriptor(BaseFieldDescriptor):
    """The field contains numbers of any kind including decimals."""

    type: Literal["number"] = "number"
    format: Optional[Literal["default"]] = None
    constraints: Optional[ValueConstraints[float]] = None

    decimal_char: Optional[str] = pydantic.Field(default=None, alias="decimalChar")
    """
    String whose value is used to represent a decimal point for number fields
    """

    group_char: Optional[str] = pydantic.Field(default=None, alias="groupChar")
    """
    String whose value is used to group digits for integer/number fields
    """

    bare_number: Optional[bool] = pydantic.Field(default=None, alias="bareNumber")
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
    constraints: StringConstraints = pydantic.Field(default_factory=StringConstraints)

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
    ArrayFieldDescriptor,
    BooleanFieldDescriptor,
    DateFieldDescriptor,
    DatetimeFieldDescriptor,
    DurationFieldDescriptor,
    GeoJSONFieldDescriptor,
    GeoPointFieldDescriptor,
    IntegerFieldDescriptor,
    ListFieldDescriptor,
    NumberFieldDescriptor,
    ObjectFieldDescriptor,
    StringFieldDescriptor,
    TimeFieldDescriptor,
    YearFieldDescriptor,
    YearmonthFieldDescriptor,
]
