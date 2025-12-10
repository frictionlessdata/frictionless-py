"""field_descriptor.py provides pydantic Models for Field descriptors"""

from __future__ import annotations

import datetime
from typing import Any, ClassVar, Dict, List, Literal, Optional, Union, Pattern
import re

from pydantic import Field as PydanticField, AliasChoices, model_validator, BaseModel
from typing_extensions import Self


from .. import settings
from .field_constraints import (
    BaseConstraints,
    CollectionConstraints,
    JSONConstraints,
    StringConstraints,
    ValueConstraints,
)

TableSchemaTypes = Union[bool, str, float, int]
"""Python equivalents of types supported by the Table schema specification"""


class BaseFieldDescriptor(BaseModel):
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

    missing_values: Optional[List[str]] = PydanticField(
        default=None, alias="missingValues"
    )
    """
    A list of field values to consider as null values
    """

    example: Optional[Any] = None
    """
    An example of a value for the field.
    """

    @model_validator(mode="before")
    @classmethod
    def compat(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        # Backward compatibility for field.format

        format_ = data.get("format")
        if format_:
            if format_.startswith("fmt:"):
                data["format"] = format_[4:]

        return data

    @model_validator(mode="after")
    def validate_example(self) -> Self:
        """Validate that the example value can be converted using read_value() if available"""
        if self.example is not None:
            if hasattr(self, "read_value"):
                read_value_method = getattr(self, "read_value")
                result = read_value_method(self.example)
                if result is None:
                    raise ValueError(
                        f'example value "{self.example}" for field "{self.name}" is not valid'
                    )

        return self


class BooleanFieldDescriptor(BaseFieldDescriptor):
    """The field contains boolean (true/false) data."""

    type: ClassVar[Literal["boolean"]] = "boolean"

    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[bool]] = None

    true_values: Optional[List[str]] = PydanticField(
        default=settings.DEFAULT_TRUE_VALUES,
        alias="trueValues",
        validation_alias=AliasChoices("trueValues", "true_values"),
    )
    """
    Values to be interpreted as “true” for boolean fields
    """

    false_values: Optional[List[str]] = PydanticField(
        default=settings.DEFAULT_FALSE_VALUES,
        alias="falseValues",
        validation_alias=AliasChoices("falseValues", "false_values"),
    )
    """
    Values to be interpreted as “false” for boolean fields
    """

    def read_value(self, cell: TableSchemaTypes) -> Optional[bool]:
        """read_value converts the physical (possibly typed) representation to
        a logical boolean representation.

        See "Data representation" in the glossary for more details.
        https://datapackage.org/standard/glossary/#data-representation

        If the physical representation is already typed as a boolean, the
        value is returned unchanged.

        If the physical representation is a string, then the string is parsed
        as a boolean depending on true_values and false_values options. `None`
        is returned if the string cannot be parsed.

        Any other typed input will return `None`.
        """
        if isinstance(cell, bool):
            return cell

        if isinstance(cell, str):
            if self.true_values and cell in self.true_values:
                return True
            if self.false_values and cell in self.false_values:
                return False

        return None

    def write_value(self, cell: Optional[bool]) -> Optional[str]:
        if self.true_values and self.false_values:
            return self.true_values[0] if cell else self.false_values[0]
        return None


class ArrayFieldDescriptor(BaseFieldDescriptor):
    """The field contains a valid JSON array."""

    type: Literal["array"] = "array"
    format: Optional[Literal["default"]] = None
    constraints: Optional[JSONConstraints] = None

    # TODO type is not accurate : array item are unnamed, not described etc
    array_item: Optional[FieldDescriptor] = PydanticField(
        default=None, alias="arrayItem"
    )


class AnyFieldDescriptor(BaseFieldDescriptor):
    """The field contains values of a unspecified or mixed type."""

    type: Literal["any"] = "any"
    format: Optional[Literal["default"]] = None
    constraints: Optional[BaseConstraints[str]] = None


class DateFieldDescriptor(BaseFieldDescriptor):
    """The field contains a date without a time."""

    type: Literal["date"] = "date"
    format: Optional[str] = None
    constraints: Optional[ValueConstraints[str]] = None

    def read_value(self, cell: Any) -> Optional[datetime.date]:
        from datetime import date, datetime
        from ..platform import platform

        if isinstance(cell, datetime):
            value_time = cell.time()
            if (
                value_time.hour == 0
                and value_time.minute == 0
                and value_time.second == 0
            ):
                return datetime(cell.year, cell.month, cell.day).date()
            else:
                return None
        if isinstance(cell, date):
            return cell
        if not isinstance(cell, str):
            return None
        try:
            format_value = self.format or "default"
            if format_value == "default":
                cell = datetime.strptime(cell, settings.DEFAULT_DATE_PATTERN).date()
            elif format_value == "any":
                cell = platform.dateutil_parser.parse(cell).date()
            else:
                cell = datetime.strptime(cell, format_value).date()
        except Exception:
            return None
        return cell

    def write_value(self, cell: Optional[datetime.date]) -> Optional[str]:
        if cell is None:
            return None
        format_value = self.format or "default"
        if format_value == settings.DEFAULT_FIELD_FORMAT:
            format_value = settings.DEFAULT_DATE_PATTERN
        return cell.strftime(format_value)


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


class CategoryDict(BaseModel):
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

    categories_ordered: Optional[bool] = PydanticField(
        default=None, alias="categoriesOrdered"
    )
    """
    When categoriesOrdered is true, implementations SHOULD regard the order of
    appearance of the values in the categories property as their natural order.
    """

    group_char: Optional[str] = PydanticField(default=None, alias="groupChar")
    """
    String whose value is used to group digits for integer/number fields
    """

    bare_number: bool = PydanticField(
        default=settings.DEFAULT_BARE_NUMBER, alias="bareNumber"
    )
    """
    If false leading and trailing non numbers will be removed for integer/number fields
    """

    pattern: ClassVar[Pattern[str]] = re.compile(r"((^[^-\d]*)|(\D*$))")

    def read_value(self, cell: Any) -> Optional[int]:
        """read_value converts the physical (possibly typed) representation to
        a logical integer representation.

        See "Data representation" in the glossary for more details.
        https://datapackage.org/standard/glossary/#data-representation

        If the physical representation is already typed as an integer, the
        value is returned unchanged.

        If the physical representation is a string, then the string is parsed
        as an integer. If `bare_number` is False, non-digit characters are
        removed first. `None` is returned if the string cannot be parsed.

        If the physical representation is a float or Decimal that represents
        a whole number, it is converted to an integer.

        Any other typed input will return `None`.
        """
        from decimal import Decimal

        if isinstance(cell, bool):
            return None

        elif isinstance(cell, int):
            return cell

        elif isinstance(cell, str):
            cell = cell.strip()

            # Process the cell (remove non-digit characters if bare_number is False)
            if not self.bare_number:
                cell = self.pattern.sub("", cell)

            # Cast the cell
            try:
                return int(cell)
            except Exception:
                return None

        elif isinstance(cell, float) and cell.is_integer():
            return int(cell)
        elif isinstance(cell, Decimal) and cell % 1 == 0:
            return int(cell)

        return None

    def write_value(self, cell: Optional[int]) -> Optional[str]:
        """write_value converts the logical integer representation to
        a physical (string) representation.

        Returns the integer as a string.
        """
        if cell is None:
            return None
        return str(cell)


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
