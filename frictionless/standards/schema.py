from __future__ import annotations
from typing import Dict, List, Union, Literal
from typing_extensions import Required, TypedDict


class ISchema(TypedDict, total=False):
    name: str
    title: str
    description: str
    fields: Required[IField]
    missingValues: List[str]
    primary_key: List[str]
    foreign_keys: List[IForeignKey]


class IBaseField(TypedDict, total=False):
    name: Required[str]
    title: str
    description: str
    format: str
    missingValues: List[str]


class IAnyField(IBaseField, total=False):
    type: Required[Literal["any"]]


class IArrayField(IBaseField, total=False):
    type: Required[Literal["array"]]
    arrayItem: Dict


class IBooleanField(IBaseField, total=False):
    type: Required[Literal["boolean"]]
    trueValues: List[str]
    falseValues: List[str]


class IDateField(IBaseField, total=False):
    type: Required[Literal["date"]]


class IDatetimeField(IBaseField, total=False):
    type: Required[Literal["datetime"]]


class IDurationField(IBaseField, total=False):
    type: Required[Literal["duration"]]


class IGeojsonField(IBaseField, total=False):
    type: Required[Literal["geojson"]]


class IGeopointField(IBaseField, total=False):
    type: Required[Literal["geopoint"]]


class IIntegerField(IBaseField, total=False):
    type: Required[Literal["integer"]]
    bareNumber: bool


class INumberField(IBaseField, total=False):
    type: Required[Literal["number"]]
    bareNumber: bool


class IObjectField(IBaseField, total=False):
    type: Required[Literal["object"]]


class IStringField(IBaseField, total=False):
    type: Required[Literal["string"]]


class ITimeField(IBaseField, total=False):
    type: Required[Literal["time"]]


class IYearField(IBaseField, total=False):
    type: Required[Literal["year"]]


class IYearmonthField(IBaseField, total=False):
    type: Required[Literal["yearmonth"]]


IField = Union[
    IAnyField,
    IArrayField,
    IBooleanField,
    IDateField,
    IDatetimeField,
    IDurationField,
    IGeojsonField,
    IGeopointField,
    IIntegerField,
    INumberField,
    IObjectField,
    IStringField,
    ITimeField,
    IYearField,
    IYearmonthField,
]


class IForeignKey(TypedDict, total=False):
    fields: Required[List[str]]
    reference: IForeignKeyReference


class IForeignKeyReference(TypedDict, total=False):
    fields: Required[List[str]]
    resource: Required[str]
