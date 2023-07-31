from __future__ import annotations

from typing import List, Union

from typing_extensions import TypedDict


# TODO: replace by frictionless-standards
class IDialect(TypedDict, total=False):
    name: str
    type: str
    title: str
    description: str
    header: bool
    headerRows: List[int]
    headerJoin: str
    headerCase: bool
    commentChar: str
    commentRows: List[int]
    skipBlankRows: bool
    csv: ICsvControl
    json: IJsonControl
    excel: IExcelControl


class IControl(TypedDict, total=False):
    name: str
    # implicit = type
    title: str
    description: str


class ICsvControl(IControl, total=False):
    delimiter: str
    lineTerminator: str
    quoteChar: str
    doubleQuote: bool
    escapeChar: str
    nullSequence: str
    skipInitialSpace: bool


class IJsonControl(IControl, total=False):
    keys: List[str]
    keyed: bool
    property: str


class IExcelControl(IControl, total=False):
    sheet: Union[str, int]
    fillMergedCells: bool
    preserveFormatting: bool
    adjustFloatingPointError: bool
    stringified: bool
