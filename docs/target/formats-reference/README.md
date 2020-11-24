# Formats Reference

It's a formats reference supported by the main Frictionless package. If you have installed external plugins, there can be more formats available. Below we're listing a format group name (or a parser name) like Excel, which is used, for example, for `xlsx`, `xls` etc formats. Options can be used for creating dialects, for example, `dialect = ExcelDialect(sheet=1)`.


## Bigquery


### Options

#### Project

> Type: str

Project

#### Dataset

> Type: str

Dataset

#### Table

> Type: str

Table



## Csv


### Options

#### Delimiter

> Type: str

Csv delimiter

#### Line Terminator

> Type: str

Csv line terminator

#### Quote Char

> Type: str

Csv quote char

#### Double Quote

> Type: bool

Csv double quote

#### Escape Char

> Type: str

Csv escape char

#### Null Sequence

> Type: str

Csv null sequence

#### Skip Initial Space

> Type: bool

Csv skip initial space

#### Comment Char

> Type: str

Csv comment char



## Excel


### Options

#### Sheet

> Type: int|str

Number from 1 or name of an excel sheet

#### Workbook Cache

> Type: dict

Workbook cache

#### Fill Merged Cells

> Type: bool

Whether to fill merged cells

#### Preserve Formatting

> Type: bool

Whither to preserve formatting

#### Adjust Floating Point Error

> Type: bool

Whether to adjust floating point error



## Gsheet


There are no options available.


## Html


### Options

#### Selector

> Type: str

Html selector



## Inline


### Options

#### Keys

> Type: str[]

A list of strings to use as data keys

#### Keyed

> Type: bool

Whether data rows are keyed



## Inline


### Options

#### Keys

> Type: str[]

A list of strings to use as data keys

#### Keyed

> Type: bool

Whether data rows are keyed



## Json


### Options

#### Keys

> Type: str[]

A list of strings to use as data keys

#### Keyed

> Type: bool

Whether data rows are keyed

#### Property

> Type: str

A path within json to the data



## Ods


### Options

#### Sheet

> Type: str

Sheet



## Pandas


There are no options available.


## Spss


There are no options available.


## Sql


### Options

#### Table

> Type: str

Table

#### Order By

> Type: str

Order_by


