from __future__ import annotations

from typing import Any, Callable, Dict, List, Literal, Optional, Protocol, Tuple

from typing_extensions import Required, TypedDict


class ISchema(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    fields: Required[IField]
    missingValues: List[str]
    primary_key: List[str]
    foreign_keys: List[IForeignKey]


class IField(TypedDict, total=False):
    name: Required[str]
    title: str
    description: str
    format: str
    missingValues: List[str]


class IAnyField(IField, total=False):
    type: Required[Literal["any"]]


class IArrayField(IField, total=False):
    type: Required[Literal["array"]]
    # support json/csv format
    arrayItem: Dict[str, Any]


class IBooleanField(IField, total=False):
    type: Required[Literal["boolean"]]
    trueValues: List[str]
    falseValues: List[str]


class IDateField(IField, total=False):
    type: Required[Literal["date"]]


class IDatetimeField(IField, total=False):
    type: Required[Literal["datetime"]]


class IDurationField(IField, total=False):
    type: Required[Literal["duration"]]


class IGeojsonField(IField, total=False):
    type: Required[Literal["geojson"]]


class IGeopointField(IField, total=False):
    type: Required[Literal["geopoint"]]


class IIntegerField(IField, total=False):
    type: Required[Literal["integer"]]
    bareNumber: bool
    groupChar: str


class INumberField(IField, total=False):
    type: Required[Literal["number"]]
    bareNumber: bool
    groupChar: str
    decimalChar: str


class IObjectField(IField, total=False):
    type: Required[Literal["object"]]


class IStringField(IField, total=False):
    type: Required[Literal["string"]]


class ITimeField(IField, total=False):
    type: Required[Literal["time"]]


class IYearField(IField, total=False):
    type: Required[Literal["year"]]


class IYearmonthField(IField, total=False):
    type: Required[Literal["yearmonth"]]


class IForeignKey(TypedDict, total=False):
    fields: Required[List[str]]
    reference: IForeignKeyReference


class IForeignKeyReference(TypedDict, total=False):
    fields: Required[List[str]]
    resource: Required[str]


INotes = Optional[Dict[str, str]]
IValueReader = Callable[[Any], Any]
IValueWriter = Callable[[Any], Any]


class ICellReader(Protocol):
    def __call__(self, cell: Any) -> Tuple[Any, INotes]:
        ...


class ICellWriter(Protocol):
    def __call__(self, cell: Any, *, ignore_missing: bool = False) -> Tuple[Any, INotes]:
        ...
