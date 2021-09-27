---
title: API Reference
---

## ApiServer

```python
class ApiServer(Server)
```

API server implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.server import ApiParser`


## BigqueryDialect

```python
class BigqueryDialect(Dialect)
```

Bigquery dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `project` _str_ - project
- `dataset?` _str_ - dataset
- `table?` _str_ - table
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## BigqueryParser

```python
class BigqueryParser(Parser)
```

Bigquery parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryParser`


## BigqueryPlugin

```python
class BigqueryPlugin(Plugin)
```

Plugin for BigQuery

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryPlugin`


## BigqueryStorage

```python
class BigqueryStorage(Storage)
```

BigQuery storage implementation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryStorage`

**Arguments**:

- `service` _object_ - BigQuery `Service` object
- `project` _str_ - BigQuery project name
- `dataset` _str_ - BigQuery dataset name
- `prefix?` _str_ - prefix for all names


## BufferControl

```python
class BufferControl(Control)
```

Buffer control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.buffer import BufferControl`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## BufferLoader

```python
class BufferLoader(Loader)
```

Buffer loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.buffer import BufferLoader`


## BufferPlugin

```python
class BufferPlugin(Plugin)
```

Plugin for Buffer Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import BufferPlugin`


## Check

```python
class Check(Metadata)
```

Check representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Checks`

It's an interface for writing Frictionless checks.

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
  

**Raises**:

- `FrictionlessException` - raise if metadata is invalid


### check.resource

```python
@property
def resource()
```

**Returns**:

- `Resource?` - resource object available after the `check.connect` call


### check.connect

```python
def connect(resource)
```

Connect to the given resource

**Arguments**:

- `resource` _Resource_ - data resource


### check.validate\_start

```python
def validate_start()
```

Called to validate the resource after opening

**Yields**:

- `Error` - found errors


### check.validate\_row

```python
def validate_row(row)
```

Called to validate the given row (on every row)

**Arguments**:

- `row` _Row_ - table row
  

**Yields**:

- `Error` - found errors


### check.validate\_end

```python
def validate_end()
```

Called to validate the resource before closing

**Yields**:

- `Error` - found errors


## CkanDialect

```python
class CkanDialect(Dialect)
```

Ckan dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ckan import CkanDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `resource?` _str_ - resource
- `dataset?` _str_ - dataset
- `apikey?` _str_ - apikey
- `fields?` _array_ - limit ckan query to certain fields
- `limit?` _int_ - limit number of returned entries
- `sort?` _str_ - sort returned entries, e.g. by date descending: `date desc`
- `filters?` _dict_ - filter data, e.g. field with value: `{ "key": "value" }`
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## CkanParser

```python
class CkanParser(Parser)
```

Ckan parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ckan import CkanParser`


## CkanPlugin

```python
class CkanPlugin(Plugin)
```

Plugin for CKAN

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ckan import CkanPlugin`


## CkanStorage

```python
class CkanStorage(Storage)
```

Ckan storage implementation

**Arguments**:

- `url` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dataset` _string_ - dataset id in CKAN e.g. "my-dataset"
- `apikey?` _str_ - API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
  
  
  API      | Usage
  -------- | --------
  Public   | `from frictionless.plugins.ckan import CkanStorage`


## Control

```python
class Control(Metadata)
```

Control representation

API      | Usage
-------- | --------
Public   | `from frictionless import Control`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## CsvDialect

```python
class CsvDialect(Dialect)
```

Csv dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.csv import CsvDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `delimiter?` _str_ - csv delimiter
- `line_terminator?` _str_ - csv line terminator
- `quote_char?` _str_ - csv quote char
- `double_quote?` _bool_ - csv double quote
- `escape_char?` _str_ - csv escape char
- `null_sequence?` _str_ - csv null sequence
- `skip_initial_space?` _bool_ - csv skip initial space
- `comment_char?` _str_ - csv comment char
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### csvDialect.delimiter

```python
@Metadata.property
def delimiter()
```

**Returns**:

- `str` - delimiter


### csvDialect.line\_terminator

```python
@Metadata.property
def line_terminator()
```

**Returns**:

- `str` - line terminator


### csvDialect.quote\_char

```python
@Metadata.property
def quote_char()
```

**Returns**:

- `str` - quote char


### csvDialect.double\_quote

```python
@Metadata.property
def double_quote()
```

**Returns**:

- `bool` - double quote


### csvDialect.escape\_char

```python
@Metadata.property
def escape_char()
```

**Returns**:

- `str?` - escape char


### csvDialect.null\_sequence

```python
@Metadata.property
def null_sequence()
```

**Returns**:

- `str?` - null sequence


### csvDialect.skip\_initial\_space

```python
@Metadata.property
def skip_initial_space()
```

**Returns**:

- `bool` - if skipping initial space


### csvDialect.comment\_char

```python
@Metadata.property
def comment_char()
```

**Returns**:

- `str?` - comment char


### csvDialect.expand

```python
def expand()
```

Expand metadata


### csvDialect.to\_python

```python
def to_python()
```

Conver to Python's `csv.Dialect`


## CsvParser

```python
class CsvParser(Parser)
```

CSV parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.csv import CsvPlugins


## CsvPlugin

```python
class CsvPlugin(Plugin)
```

Plugin for Pandas

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.csv import CsvPlugin`


## Detector

```python
class Detector()
```

Detector representation

API      | Usage
-------- | --------
Public   | `from frictionless import Detector`

**Arguments**:

  
- `buffer_size?` _int_ - The amount of bytes to be extracted as a buffer.
  It defaults to 10000
  
- `sample_size?` _int_ - The amount of rows to be extracted as a samle.
  It defaults to 100
  
- `field_type?` _str_ - Enforce all the inferred types to be this type.
  For more information, please check "Describing  Data" guide.
  
- `field_names?` _str[]_ - Enforce all the inferred fields to have provided names.
  For more information, please check "Describing  Data" guide.
  
- `field_confidence?` _float_ - A number from 0 to 1 setting the infer confidence.
  If  1 the data is guaranteed to be valid against the inferred schema.
  For more information, please check "Describing  Data" guide.
  It defaults to 0.9
  
- `field_float_numbers?` _bool_ - Flag to indicate desired number type.
  By default numbers will be `Decimal`; if `True` - `float`.
  For more information, please check "Describing  Data" guide.
  It defaults to `False`
  
- `field_missing_values?` _str[]_ - String to be considered as missing values.
  For more information, please check "Describing  Data" guide.
  It defaults to `['']`
  
- `schema_sync?` _bool_ - Whether to sync the schema.
  If it sets to `True` the provided schema will be mapped to
  the inferred schema. It means that, for example, you can
  provide a subset of fileds to be applied on top of the inferred
  fields or the provided schema can have different order of fields.
  
- `schema_patch?` _dict_ - A dictionary to be used as an inferred schema patch.
  The form of this dictionary should follow the Schema descriptor form
  except for the `fields` property which should be a mapping with the
  key named after a field name and the values being a field patch.
  For more information, please check "Extracting Data" guide.


### detector.detect\_encoding

```python
def detect_encoding(buffer, *, encoding=None)
```

Detect encoding from buffer

**Arguments**:

- `buffer` _byte_ - byte buffer
  

**Returns**:

- `str` - encoding


### detector.detect\_layout

```python
def detect_layout(sample, *, layout=None)
```

Detect layout from sample

**Arguments**:

- `sample` _any[][]_ - data sample
- `layout?` _Layout_ - data layout
  

**Returns**:

- `Layout` - layout


### detector.detect\_schema

```python
def detect_schema(fragment, *, labels=None, schema=None)
```

Detect schema from fragment

**Arguments**:

- `fragment` _any[][]_ - data fragment
- `labels?` _str[]_ - data labels
- `schema?` _Schema_ - data schema
  

**Returns**:

- `Schema` - schema


## Dialect

```python
class Dialect(Metadata)
```

Dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless import Dialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## Error

```python
class Error(Metadata)
```

Error representation

API      | Usage
-------- | --------
Public   | `from frictionless import errors`

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### error.note

```python
@property
def note()
```

**Returns**:

- `str` - note


### error.message

```python
@property
def message()
```

**Returns**:

- `str` - message


## ExcelDialect

```python
class ExcelDialect(Dialect)
```

Excel dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import ExcelDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `sheet?` _int|str_ - number from 1 or name of an excel sheet
- `workbook_cache?` _dict_ - workbook cache
- `fill_merged_cells?` _bool_ - whether to fill merged cells
- `preserve_formatting?` _bool_ - whither to preserve formatting
- `adjust_floating_point_error?` _bool_ - whether to adjust floating point error
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### excelDialect.sheet

```python
@Metadata.property
def sheet()
```

**Returns**:

- `str|int` - sheet


### excelDialect.workbook\_cache

```python
@Metadata.property
def workbook_cache()
```

**Returns**:

- `dict` - workbook cache


### excelDialect.fill\_merged\_cells

```python
@Metadata.property
def fill_merged_cells()
```

**Returns**:

- `bool` - fill merged cells


### excelDialect.preserve\_formatting

```python
@Metadata.property
def preserve_formatting()
```

**Returns**:

- `bool` - preserve formatting


### excelDialect.adjust\_floating\_point\_error

```python
@Metadata.property
def adjust_floating_point_error()
```

**Returns**:

- `bool` - adjust floating point error


### excelDialect.expand

```python
def expand()
```

Expand metadata


## ExcelPlugin

```python
class ExcelPlugin(Plugin)
```

Plugin for Excel

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import ExcelPlugin`


## Field

```python
class Field(Metadata)
```

Field representation

API      | Usage
-------- | --------
Public   | `from frictionless import Field`

**Arguments**:

- `descriptor?` _str|dict_ - field descriptor
- `name?` _str_ - field name (for machines)
- `title?` _str_ - field title (for humans)
- `description?` _str_ - field description
- `type?` _str_ - field type e.g. `string`
- `format?` _str_ - field format e.g. `default`
- `missing_values?` _str[]_ - missing values
- `constraints?` _dict_ - constraints
- `rdf_type?` _str_ - RDF type
- `schema?` _Schema_ - parent schema object
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### field.name

```python
@Metadata.property
def name()
```

**Returns**:

- `str` - name


### field.title

```python
@Metadata.property
def title()
```

**Returns**:

- `str` - title


### field.description

```python
@Metadata.property
def description()
```

**Returns**:

- `str` - description


### field.description\_html

```python
@Metadata.property(cache=False, write=False)
def description_html()
```

**Returns**:

- `str` - field description


### field.description\_text

```python
@Metadata.property
def description_text()
```

**Returns**:

- `str` - field description


### field.type

```python
@Metadata.property
def type()
```

**Returns**:

- `str` - type


### field.format

```python
@Metadata.property
def format()
```

**Returns**:

- `str` - format


### field.missing\_values

```python
@Metadata.property
def missing_values()
```

**Returns**:

- `str[]` - missing values


### field.constraints

```python
@Metadata.property
def constraints()
```

**Returns**:

- `dict` - constraints


### field.rdf\_type

```python
@Metadata.property
def rdf_type()
```

**Returns**:

- `str` - RDF Type


### field.required

```python
@Metadata.property(
        write=lambda self, value: setitem(self.constraints, "required", value)
    )
def required()
```

**Returns**:

- `bool` - if field is requried


### field.builtin

```python
@property
def builtin()
```

**Returns**:

- `bool` - returns True is the type is not custom


### field.schema

```python
@property
def schema()
```

**Returns**:

- `Schema?` - parent schema


### field.array\_item

```python
@Metadata.property
def array_item()
```

**Returns**:

- `dict` - field descriptor


### field.array\_item\_field

```python
@Metadata.property(write=False)
def array_item_field()
```

**Returns**:

- `dict` - field descriptor


### field.true\_values

```python
@Metadata.property
def true_values()
```

**Returns**:

- `str[]` - true values


### field.false\_values

```python
@Metadata.property
def false_values()
```

**Returns**:

- `str[]` - false values


### field.bare\_number

```python
@Metadata.property
def bare_number()
```

**Returns**:

- `bool` - if a bare number


### field.float\_number

```python
@Metadata.property
def float_number()
```

**Returns**:

- `bool` - whether it's a floating point number


### field.decimal\_char

```python
@Metadata.property
def decimal_char()
```

**Returns**:

- `str` - decimal char


### field.group\_char

```python
@Metadata.property
def group_char()
```

**Returns**:

- `str` - group char


### field.expand

```python
def expand()
```

Expand metadata


### field.read\_cell

```python
def read_cell(cell)
```

Read cell

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

  (any, OrderedDict): processed cell and dict of notes


### field.read\_cell\_convert

```python
def read_cell_convert(cell)
```

Read cell (convert only)

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

- `any/None` - processed cell or None if an error


### field.read\_cell\_checks

```python
@Metadata.property(write=False)
def read_cell_checks()
```

Read cell (checks only)

**Returns**:

- `OrderedDict` - dictionlary of check function by a constraint name


### field.write\_cell

```python
def write_cell(cell, *, ignore_missing=False)
```

Write cell

**Arguments**:

- `cell` _any_ - cell to convert
- `ignore_missing?` _bool_ - don't convert None values
  

**Returns**:

  (any, OrderedDict): processed cell and dict of notes


### field.write\_cell\_convert

```python
def write_cell_convert(cell)
```

Write cell (convert only)

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

- `any/None` - processed cell or None if an error


### field.write\_cell\_missing\_value

```python
@Metadata.property(write=False)
def write_cell_missing_value()
```

Write cell (missing value only)

**Returns**:

- `str` - a value to replace None cells


## File

```python
class File()
```

File representation


## FrictionlessException

```python
class FrictionlessException(Exception)
```

Main Frictionless exception

API      | Usage
-------- | --------
Public   | `from frictionless import FrictionlessException`

**Arguments**:

- `error` _Error_ - an underlaying error


### frictionlessException.error

```python
@property
def error()
```

**Returns**:

- `Error` - error


## GsheetsDialect

```python
class GsheetsDialect(Dialect)
```

Gsheets dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheets import GsheetsDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### gsheetsDialect.credentials

```python
@Metadata.property
def credentials()
```

**Returns**:

- `str` - credentials


## GsheetsParser

```python
class GsheetsParser(Parser)
```

Google Sheets parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheets import GsheetsParser`


## GsheetsPlugin

```python
class GsheetsPlugin(Plugin)
```

Plugin for Google Sheets

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheets import GsheetsPlugin`


## Header

```python
class Header(list)
```

Header representation

API      | Usage
-------- | --------
Public   | `from frictionless import Header`

> Constructor of this object is not Public API

**Arguments**:

- `labels` _any[]_ - header row labels
- `fields` _Field[]_ - table fields
- `field_positions` _int[]_ - field positions
- `row_positions` _int[]_ - row positions
- `ignore_case` _bool_ - ignore case


### header.labels

```python
@cached_property
def labels()
```

**Returns**:

- `Schema` - table labels


### header.fields

```python
@cached_property
def fields()
```

**Returns**:

- `Schema` - table fields


### header.field\_names

```python
@cached_property
def field_names()
```

**Returns**:

- `str[]` - table field names


### header.field\_positions

```python
@cached_property
def field_positions()
```

**Returns**:

- `int[]` - table field positions


### header.row\_positions

```python
@cached_property
def row_positions()
```

**Returns**:

- `int[]` - table row positions


### header.missing

```python
@cached_property
def missing()
```

**Returns**:

- `bool` - if there is not header


### header.errors

```python
@cached_property
def errors()
```

**Returns**:

- `Error[]` - header errors


### header.valid

```python
@cached_property
def valid()
```

**Returns**:

- `bool` - if header valid


### header.to\_str

```python
def to_str()
```

**Returns**:

- `str` - a row as a CSV string


### header.to\_list

```python
def to_list()
```

Convert to a list


## HtmlDialect

```python
class HtmlDialect(Dialect)
```

Html dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `selector?` _str_ - HTML selector
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### htmlDialect.selector

```python
@Metadata.property
def selector()
```

**Returns**:

- `str` - selector


### htmlDialect.expand

```python
def expand()
```

Expand metadata


## HtmlParser

```python
class HtmlParser(Parser)
```

HTML parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlParser`


## HtmlPlugin

```python
class HtmlPlugin(Plugin)
```

Plugin for HTML

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlPlugin`


## InlineDialect

```python
class InlineDialect(Dialect)
```

Inline dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.inline import InlineDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `keys?` _str[]_ - a list of strings to use as data keys
- `keyed?` _bool_ - whether data rows are keyed
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### inlineDialect.keys

```python
@Metadata.property
def keys()
```

**Returns**:

- `str[]?` - keys


### inlineDialect.keyed

```python
@Metadata.property
def keyed()
```

**Returns**:

- `bool` - keyed


### inlineDialect.expand

```python
def expand()
```

Expand metadata


## InlineParser

```python
class InlineParser(Parser)
```

Inline parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.inline import InlineParser


## InlinePlugin

```python
class InlinePlugin(Plugin)
```

Plugin for Inline

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.inline import InlinePlugin`


## Inquiry

```python
class Inquiry(Metadata)
```

Inquiry representation.

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### inquiry.tasks

```python
@property
def tasks()
```

**Returns**:

- `dict[]` - tasks


## InquiryTask

```python
class InquiryTask(Metadata)
```

Inquiry task representation.

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### inquiryTask.source

```python
@property
def source()
```

**Returns**:

- `any` - source


### inquiryTask.type

```python
@property
def type()
```

**Returns**:

- `string?` - type


## JsonDialect

```python
class JsonDialect(Dialect)
```

Json dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `keys?` _str[]_ - a list of strings to use as data keys
- `keyed?` _bool_ - whether data rows are keyed
- `property?` _str_ - a path within JSON to the data
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### jsonDialect.keys

```python
@Metadata.property
def keys()
```

**Returns**:

- `str[]?` - keys


### jsonDialect.keyed

```python
@Metadata.property
def keyed()
```

**Returns**:

- `bool` - keyed


### jsonDialect.property

```python
@Metadata.property
def property()
```

**Returns**:

- `str?` - property


### jsonDialect.expand

```python
def expand()
```

Expand metadata


## JsonParser

```python
class JsonParser(Parser)
```

JSON parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonParser


## JsonPlugin

```python
class JsonPlugin(Plugin)
```

Plugin for Json

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonPlugin`


## JsonlParser

```python
class JsonlParser(Parser)
```

JSONL parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonlParser


## Layout

```python
class Layout(Metadata)
```

Layout representation

API      | Usage
-------- | --------
Public   | `from frictionless import Layout`

**Arguments**:

- `descriptor?` _str|dict_ - layout descriptor
  pick_fields? ((str|int)[]): what fields to pick
  skip_fields? ((str|int)[]): what fields to skip
- `limit_fields?` _int_ - amount of fields
- `offset_fields?` _int_ - from what field to start
  pick_rows? ((str|int)[]): what rows to pick
  skip_rows? ((str|int)[]): what rows to skip
- `limit_rows?` _int_ - amount of rows
- `offset_rows?` _int_ - from what row to start


### layout.header

```python
@Metadata.property
def header()
```

**Returns**:

- `bool` - if there is a header row


### layout.header\_rows

```python
@Metadata.property
def header_rows()
```

**Returns**:

- `int[]` - header rows


### layout.header\_join

```python
@Metadata.property
def header_join()
```

**Returns**:

- `str` - header joiner


### layout.header\_case

```python
@Metadata.property
def header_case()
```

**Returns**:

- `str` - header case sensitive


### layout.pick\_fields

```python
@Metadata.property
def pick_fields()
```

**Returns**:

- `(str|int)[]?` - pick fields


### layout.skip\_fields

```python
@Metadata.property
def skip_fields()
```

**Returns**:

- `(str|int)[]?` - skip fields


### layout.limit\_fields

```python
@Metadata.property
def limit_fields()
```

**Returns**:

- `int?` - limit fields


### layout.offset\_fields

```python
@Metadata.property
def offset_fields()
```

**Returns**:

- `int?` - offset fields


### layout.pick\_rows

```python
@Metadata.property
def pick_rows()
```

**Returns**:

- `(str|int)[]?` - pick rows


### layout.skip\_rows

```python
@Metadata.property
def skip_rows()
```

**Returns**:

- `(str|int)[]?` - skip rows


### layout.limit\_rows

```python
@Metadata.property
def limit_rows()
```

**Returns**:

- `int?` - limit rows


### layout.offset\_rows

```python
@Metadata.property
def offset_rows()
```

**Returns**:

- `int?` - offset rows


### layout.is\_field\_filtering

```python
@Metadata.property(write=False)
def is_field_filtering()
```

**Returns**:

- `bool` - whether there is a field filtering


### layout.pick\_fields\_compiled

```python
@Metadata.property(write=False)
def pick_fields_compiled()
```

**Returns**:

- `re?` - compiled pick fields


### layout.skip\_fields\_compiled

```python
@Metadata.property(write=False)
def skip_fields_compiled()
```

**Returns**:

- `re?` - compiled skip fields


### layout.pick\_rows\_compiled

```python
@Metadata.property(write=False)
def pick_rows_compiled()
```

**Returns**:

- `re?` - compiled pick rows


### layout.skip\_rows\_compiled

```python
@Metadata.property(write=False)
def skip_rows_compiled()
```

**Returns**:

- `re?` - compiled skip fields


### layout.expand

```python
def expand()
```

Expand metadata


## Loader

```python
class Loader()
```

Loader representation

API      | Usage
-------- | --------
Public   | `from frictionless import Loader`

**Arguments**:

- `resource` _Resource_ - resource


### loader.resource

```python
@property
def resource()
```

**Returns**:

- `resource` _Resource_ - resource


### loader.buffer

```python
@property
def buffer()
```

**Returns**:

- `Loader` - buffer


### loader.byte\_stream

```python
@property
def byte_stream()
```

Resource byte stream

The stream is available after opening the loader

**Returns**:

- `io.ByteStream` - resource byte stream


### loader.text\_stream

```python
@property
def text_stream()
```

Resource text stream

The stream is available after opening the loader

**Returns**:

- `io.TextStream` - resource text stream


### loader.open

```python
def open()
```

Open the loader as "io.open" does


### loader.close

```python
def close()
```

Close the loader as "filelike.close" does


### loader.closed

```python
@property
def closed()
```

Whether the loader is closed

**Returns**:

- `bool` - if closed


### loader.read\_byte\_stream

```python
def read_byte_stream()
```

Read bytes stream

**Returns**:

- `io.ByteStream` - resource byte stream


### loader.read\_byte\_stream\_create

```python
def read_byte_stream_create()
```

Create bytes stream

**Returns**:

- `io.ByteStream` - resource byte stream


### loader.read\_byte\_stream\_process

```python
def read_byte_stream_process(byte_stream)
```

Process byte stream

**Arguments**:

- `byte_stream` _io.ByteStream_ - resource byte stream
  

**Returns**:

- `io.ByteStream` - resource byte stream


### loader.read\_byte\_stream\_decompress

```python
def read_byte_stream_decompress(byte_stream)
```

Decompress byte stream

**Arguments**:

- `byte_stream` _io.ByteStream_ - resource byte stream
  

**Returns**:

- `io.ByteStream` - resource byte stream


### loader.read\_byte\_stream\_buffer

```python
def read_byte_stream_buffer(byte_stream)
```

Buffer byte stream

**Arguments**:

- `byte_stream` _io.ByteStream_ - resource byte stream
  

**Returns**:

- `bytes` - buffer


### loader.read\_byte\_stream\_analyze

```python
def read_byte_stream_analyze(buffer)
```

Detect metadta using sample

**Arguments**:

- `buffer` _bytes_ - byte buffer


### loader.read\_text\_stream

```python
def read_text_stream()
```

Read text stream

**Returns**:

- `io.TextStream` - resource text stream


### loader.write\_byte\_stream

```python
def write_byte_stream(path)
```

Write from a temporary file

**Arguments**:

- `path` _str_ - path to a temporary file
  

**Returns**:

- `any` - result of writing e.g. resulting path


### loader.write\_byte\_stream\_create

```python
def write_byte_stream_create(path)
```

Create byte stream for writing

**Arguments**:

- `path` _str_ - path to a temporary file
  

**Returns**:

- `io.ByteStream` - byte stream


### loader.write\_byte\_stream\_save

```python
def write_byte_stream_save(byte_stream)
```

Store byte stream


## LocalControl

```python
class LocalControl(Control)
```

Local control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import LocalControl`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## LocalLoader

```python
class LocalLoader(Loader)
```

Local loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import LocalLoader`


## LocalPlugin

```python
class LocalPlugin(Plugin)
```

Plugin for Local Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import LocalPlugin`


## Metadata

```python
class Metadata(helpers.ControlledDict)
```

Metadata representation

API      | Usage
-------- | --------
Public   | `from frictionless import Metadata`

**Arguments**:

- `descriptor?` _str|dict_ - metadata descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### metadata.setinitial

```python
def setinitial(key, value)
```

Set an initial item in a subclass' constructor

**Arguments**:

- `key` _str_ - key
- `value` _any_ - value


### metadata.to\_copy

```python
def to_copy()
```

Create a copy of the metadata

**Returns**:

- `Metadata` - a copy of the metadata


### metadata.to\_dict

```python
def to_dict()
```

Convert metadata to a plain dict

**Returns**:

- `dict` - metadata as a plain dict


### metadata.to\_json

```python
def to_json(path=None, encoder_class=None)
```

Save metadata as a json

**Arguments**:

- `path` _str_ - target path
  

**Raises**:

- `FrictionlessException` - on any error


### metadata.to\_yaml

```python
def to_yaml(path=None)
```

Save metadata as a yaml

**Arguments**:

- `path` _str_ - target path
  

**Raises**:

- `FrictionlessException` - on any error


### metadata.metadata\_valid

```python
@property
def metadata_valid()
```

**Returns**:

- `bool` - whether the metadata is valid


### metadata.metadata\_errors

```python
@property
def metadata_errors()
```

**Returns**:

- `Errors[]` - a list of the metadata errors


### metadata.metadata\_attach

```python
def metadata_attach(name, value)
```

Helper method for attaching a value to  the metadata

**Arguments**:

- `name` _str_ - name
- `value` _any_ - value


### metadata.metadata\_extract

```python
def metadata_extract(descriptor)
```

Helper method called during the metadata extraction

**Arguments**:

- `descriptor` _any_ - descriptor


### metadata.metadata\_process

```python
def metadata_process()
```

Helper method called on any metadata change


### metadata.metadata\_validate

```python
def metadata_validate(profile=None)
```

Helper method called on any metadata change

**Arguments**:

- `profile` _dict_ - a profile to validate against of


### metadata.property

```python
@staticmethod
def property(func=None, *, cache=True, reset=True, write=True)
```

Create a metadata property

**Arguments**:

- `func` _func_ - method
- `cache?` _bool_ - cache
- `reset?` _bool_ - reset
- `write?` _func_ - write


## MultipartControl

```python
class MultipartControl(Control)
```

Multipart control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.multipart import MultipartControl`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### multipartControl.expand

```python
def expand()
```

Expand metadata


## MultipartLoader

```python
class MultipartLoader(Loader)
```

Multipart loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.multipart import MultipartLoader`


## MultipartPlugin

```python
class MultipartPlugin(Plugin)
```

Plugin for Multipart Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.multipart import MultipartPlugin`


## OdsDialect

```python
class OdsDialect(Dialect)
```

Ods dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `sheet?` _str_ - sheet
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### odsDialect.sheet

```python
@Metadata.property
def sheet()
```

**Returns**:

- `int|str` - sheet


### odsDialect.expand

```python
def expand()
```

Expand metadata


## OdsParser

```python
class OdsParser(Parser)
```

ODS parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsParser`


## OdsPlugin

```python
class OdsPlugin(Plugin)
```

Plugin for ODS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsPlugin`


## Package

```python
class Package(Metadata)
```

Package representation

API      | Usage
-------- | --------
Public   | `from frictionless import Package`

This class is one of the cornerstones of of Frictionless framework.
It manages underlaying resource and provides an ability to describe a package.


```python
package = Package(resources=[Resource(path="data/table.csv")])
package.get_resoure('table').read_rows() == [
    {'id': 1, 'name': 'english'},
    {'id': 2, 'name': '中国人'},
]
```

**Arguments**:

  
- `source` _any_ - Source of the package; can be in various forms.
  Usually, it's a package descriptor in a form of dict or path
  Also, it can be a glob pattern or a resource path
  
- `descriptor` _dict|str_ - A resource descriptor provided explicitly.
  Keyword arguments will patch this descriptor if provided.
  
- `resources?` _dict|Resource[]_ - A list of resource descriptors.
  It can be dicts or Resource instances.
  
- `id?` _str_ - A property reserved for globally unique identifiers.
  Examples of identifiers that are unique include UUIDs and DOIs.
  
- `name?` _str_ - A short url-usable (and preferably human-readable) name.
  This MUST be lower-case and contain only alphanumeric characters
  along with “.”, “_” or “-” characters.
  
- `title?` _str_ - A Package title according to the specs
  It should a human-oriented title of the resource.
  
- `description?` _str_ - A Package description according to the specs
  It should a human-oriented description of the resource.
  
- `licenses?` _dict[]_ - The license(s) under which the package is provided.
  If omitted it's considered the same as the package's licenses.
  
- `sources?` _dict[]_ - The raw sources for this data package.
  It MUST be an array of Source objects.
  Each Source object MUST have a title and
  MAY have path and/or email properties.
  
- `profile?` _str_ - A string identifying the profile of this descriptor.
  For example, `fiscal-data-package`.
  
- `homepage?` _str_ - A URL for the home on the web that is related to this package.
  For example, github repository or ckan dataset address.
  
- `version?` _str_ - A version string identifying the version of the package.
  It should conform to the Semantic Versioning requirements and
  should follow the Data Package Version pattern.
  
- `contributors?` _dict[]_ - The people or organizations who contributed to this package.
  It MUST be an array. Each entry is a Contributor and MUST be an object.
  A Contributor MUST have a title property and MAY contain
  path, email, role and organization properties.
  
- `keywords?` _str[]_ - An Array of string keywords to assist users searching.
  For example, ['data', 'fiscal']
  
- `image?` _str_ - An image to use for this data package.
  For example, when showing the package in a listing.
  
- `created?` _str_ - The datetime on which this was created.
  The datetime must conform to the string formats for RFC3339 datetime,
  
- `innerpath?` _str_ - A ZIP datapackage descriptor inner path.
  Path to the package descriptor inside the ZIP datapackage.
- `Example` - some/folder/datapackage.yaml
- `Default` - datapackage.json
  
- `basepath?` _str_ - A basepath of the resource
  The fullpath of the resource is joined `basepath` and /path`
  
- `detector?` _Detector_ - File/table detector.
  For more information, please check the Detector documentation.
  
- `onerror?` _ignore|warn|raise_ - Behaviour if there is an error.
  It defaults to 'ignore'. The default mode will ignore all errors
  on resource level and they should be handled by the user
  being available in Header and Row objects.
  
- `trusted?` _bool_ - Don't raise an exception on unsafe paths.
  A path provided as a part of the descriptor considered unsafe
  if there are path traversing or the path is absolute.
  A path provided as `source` or `path` is alway trusted.
  
- `hashing?` _str_ - a hashing algorithm for resources
  It defaults to 'md5'.
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### package.name

```python
@Metadata.property
def name()
```

**Returns**:

- `str` - package name


### package.id

```python
@Metadata.property
def id()
```

**Returns**:

- `str` - package id


### package.licenses

```python
@Metadata.property
def licenses()
```

**Returns**:

- `dict[]` - package licenses


### package.profile

```python
@Metadata.property
def profile()
```

**Returns**:

- `str` - package profile


### package.title

```python
@Metadata.property
def title()
```

**Returns**:

- `str` - package title


### package.description

```python
@Metadata.property
def description()
```

**Returns**:

- `str` - package description


### package.description\_html

```python
@Metadata.property(cache=False, write=False)
def description_html()
```

**Returns**:

- `str` - package description


### package.description\_text

```python
@Metadata.property
def description_text()
```

**Returns**:

- `str` - package description


### package.homepage

```python
@Metadata.property
def homepage()
```

**Returns**:

- `str` - package homepage


### package.version

```python
@Metadata.property
def version()
```

**Returns**:

- `str` - package version


### package.sources

```python
@Metadata.property
def sources()
```

**Returns**:

- `dict[]` - package sources


### package.contributors

```python
@Metadata.property
def contributors()
```

**Returns**:

- `dict[]` - package contributors


### package.keywords

```python
@Metadata.property
def keywords()
```

**Returns**:

- `str[]` - package keywords


### package.image

```python
@Metadata.property
def image()
```

**Returns**:

- `str` - package image


### package.created

```python
@Metadata.property
def created()
```

**Returns**:

- `str` - package created


### package.hashing

```python
@Metadata.property(cache=False, write=False)
def hashing()
```

**Returns**:

- `str` - package hashing


### package.basepath

```python
@Metadata.property(cache=False, write=False)
def basepath()
```

**Returns**:

- `str` - package basepath


### package.onerror

```python
@Metadata.property(cache=False, write=False)
def onerror()
```

**Returns**:

- `ignore|warn|raise` - on error bahaviour


### package.trusted

```python
@Metadata.property(cache=False, write=False)
def trusted()
```

**Returns**:

- `str` - package trusted


### package.resources

```python
@Metadata.property
def resources()
```

**Returns**:

- `Resources[]` - package resource


### package.resource\_names

```python
@Metadata.property(cache=False, write=False)
def resource_names()
```

**Returns**:

- `str[]` - package resource names


### package.add\_resource

```python
def add_resource(source=None, **options)
```

Add new resource to the package.

**Arguments**:

- `source` _dict|str_ - a data source
- `**options` _dict_ - options of the Resource class
  

**Returns**:

- `Resource/None` - added `Resource` instance or `None` if not added


### package.get\_resource

```python
def get_resource(name)
```

Get resource by name.

**Arguments**:

- `name` _str_ - resource name
  

**Raises**:

- `FrictionlessException` - if resource is not found
  

**Returns**:

- `Resource/None` - `Resource` instance or `None` if not found


### package.has\_resource

```python
def has_resource(name)
```

Check if a resource is present

**Arguments**:

- `name` _str_ - schema resource name
  

**Returns**:

- `bool` - whether there is the resource


### package.remove\_resource

```python
def remove_resource(name)
```

Remove resource by name.

**Arguments**:

- `name` _str_ - resource name
  

**Raises**:

- `FrictionlessException` - if resource is not found
  

**Returns**:

- `Resource/None` - removed `Resource` instances or `None` if not found


### package.expand

```python
def expand()
```

Expand metadata

It will add default values to the package.


### package.infer

```python
def infer(*, stats=False)
```

Infer package's attributes

**Arguments**:

- `stats?` _bool_ - stream files completely and infer stats


### package.to\_copy

```python
def to_copy()
```

Create a copy of the package


### package.from\_bigquery

```python
@staticmethod
def from_bigquery(source, *, dialect=None)
```

Import package from Bigquery

**Arguments**:

- `source` _string_ - BigQuery `Service` object
- `dialect` _dict_ - BigQuery dialect
  

**Returns**:

- `Package` - package


### package.to\_bigquery

```python
def to_bigquery(target, *, dialect=None)
```

Export package to Bigquery

**Arguments**:

- `target` _string_ - BigQuery `Service` object
- `dialect` _dict_ - BigQuery dialect
  

**Returns**:

- `BigqueryStorage` - storage


### package.from\_ckan

```python
@staticmethod
def from_ckan(source, *, dialect=None)
```

Import package from CKAN

**Arguments**:

- `source` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dialect` _dict_ - CKAN dialect
  

**Returns**:

- `Package` - package


### package.to\_ckan

```python
def to_ckan(target, *, dialect=None)
```

Export package to CKAN

**Arguments**:

- `target` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dialect` _dict_ - CKAN dialect
  

**Returns**:

- `CkanStorage` - storage


### package.from\_sql

```python
@staticmethod
def from_sql(source, *, dialect=None)
```

Import package from SQL

**Arguments**:

- `source` _any_ - SQL connection string of engine
- `dialect` _dict_ - SQL dialect
  

**Returns**:

- `Package` - package


### package.to\_sql

```python
def to_sql(target, *, dialect=None)
```

Export package to SQL

**Arguments**:

- `target` _any_ - SQL connection string of engine
- `dialect` _dict_ - SQL dialect
  

**Returns**:

- `SqlStorage` - storage


### package.from\_zip

```python
@staticmethod
def from_zip(path, **options)
```

Create a package from ZIP

**Arguments**:

- `path(str)` - file path
- `**options(dict)` - resouce options


### package.to\_zip

```python
def to_zip(path, *, encoder_class=None)
```

Save package to a zip

**Arguments**:

- `path` _str_ - target path
- `encoder_class` _object_ - json encoder class
  

**Raises**:

- `FrictionlessException` - on any error


## PandasDialect

```python
class PandasDialect(Dialect)
```

Pandas dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## PandasParser

```python
class PandasParser(Parser)
```

Pandas parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasParser`


## PandasPlugin

```python
class PandasPlugin(Plugin)
```

Plugin for Pandas

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasPlugin`


## Parser

```python
class Parser()
```

Parser representation

API      | Usage
-------- | --------
Public   | `from frictionless import Parser`

**Arguments**:

- `resource` _Resource_ - resource


### parser.resource

```python
@property
def resource()
```

**Returns**:

- `Resource` - resource


### parser.loader

```python
@property
def loader()
```

**Returns**:

- `Loader` - loader


### parser.sample

```python
@property
def sample()
```

**Returns**:

- `Loader` - sample


### parser.list\_stream

```python
@property
def list_stream()
```

**Yields**:

- `any[][]` - list stream


### parser.open

```python
def open()
```

Open the parser as "io.open" does


### parser.close

```python
def close()
```

Close the parser as "filelike.close" does


### parser.closed

```python
@property
def closed()
```

Whether the parser is closed

**Returns**:

- `bool` - if closed


### parser.read\_loader

```python
def read_loader()
```

Create and open loader

**Returns**:

- `Loader` - loader


### parser.read\_list\_stream

```python
def read_list_stream()
```

Read list stream

**Returns**:

- `gen<any[][]>` - list stream


### parser.read\_list\_stream\_create

```python
def read_list_stream_create()
```

Create list stream from loader

**Arguments**:

- `loader` _Loader_ - loader
  

**Returns**:

- `gen<any[][]>` - list stream


### parser.read\_list\_stream\_handle\_errors

```python
def read_list_stream_handle_errors(list_stream)
```

Wrap list stream into error handler

**Arguments**:

- `gen<any[][]>` - list stream
  

**Returns**:

- `gen<any[][]>` - list stream


### parser.write\_row\_stream

```python
def write_row_stream(resource)
```

Write row stream from the source resource

**Arguments**:

- `source` _Resource_ - source resource


## Pipeline

```python
class Pipeline(Metadata)
```

Pipeline representation.

**Arguments**:

- `descriptor?` _str|dict_ - pipeline descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### pipeline.tasks

```python
@property
def tasks()
```

**Returns**:

- `dict[]` - tasks


### pipeline.run

```python
def run(*, parallel=False)
```

Run the pipeline


## PipelineTask

```python
class PipelineTask(Metadata)
```

Pipeline task representation.

**Arguments**:

- `descriptor?` _str|dict_ - pipeline task descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### pipelineTask.run

```python
def run()
```

Run the task


## Plugin

```python
class Plugin()
```

Plugin representation

API      | Usage
-------- | --------
Public   | `from frictionless import Plugin`

It's an interface for writing Frictionless plugins.
You can implement one or more methods to hook into Frictionless system.


### plugin.create\_candidates

```python
def create_candidates(candidates)
```

Create candidates

**Returns**:

- `dict[]` - an ordered by priority list of type descriptors for type detection


### plugin.create\_check

```python
def create_check(name, *, descriptor=None)
```

Create check

**Arguments**:

- `name` _str_ - check name
- `descriptor` _dict_ - check descriptor
  

**Returns**:

- `Check` - check


### plugin.create\_control

```python
def create_control(file, *, descriptor)
```

Create control

**Arguments**:

- `file` _File_ - control file
- `descriptor` _dict_ - control descriptor
  

**Returns**:

- `Control` - control


### plugin.create\_dialect

```python
def create_dialect(file, *, descriptor)
```

Create dialect

**Arguments**:

- `file` _File_ - dialect file
- `descriptor` _dict_ - dialect descriptor
  

**Returns**:

- `Dialect` - dialect


### plugin.create\_error

```python
def create_error(descriptor)
```

Create error

**Arguments**:

- `descriptor` _dict_ - error descriptor
  

**Returns**:

- `Error` - error


### plugin.create\_file

```python
def create_file(source, **options)
```

Create file

**Arguments**:

- `source` _any_ - file source
- `options` _dict_ - file options
  

**Returns**:

- `File` - file


### plugin.create\_loader

```python
def create_loader(file)
```

Create loader

**Arguments**:

- `file` _File_ - loader file
  

**Returns**:

- `Loader` - loader


### plugin.create\_parser

```python
def create_parser(file)
```

Create parser

**Arguments**:

- `file` _File_ - parser file
  

**Returns**:

- `Parser` - parser


### plugin.create\_server

```python
def create_server(name)
```

Create server

**Arguments**:

- `name` _str_ - server name
  

**Returns**:

- `Server` - server


### plugin.create\_step

```python
def create_step(descriptor)
```

Create step

**Arguments**:

- `descriptor` _dict_ - step descriptor
  

**Returns**:

- `Step` - step


### plugin.create\_storage

```python
def create_storage(name, source, **options)
```

Create storage

**Arguments**:

- `name` _str_ - storage name
- `options` _str_ - storage options
  

**Returns**:

- `Storage` - storage


### plugin.create\_type

```python
def create_type(field)
```

Create type

**Arguments**:

- `field` _Field_ - corresponding field
  

**Returns**:

- `Type` - type


## RemoteControl

```python
class RemoteControl(Control)
```

Remote control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.remote import RemoteControl`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `http_session?` _requests.Session_ - user defined HTTP session
- `http_preload?` _bool_ - don't use HTTP streaming and preload all the data
- `http_timeout?` _int_ - user defined HTTP timeout in minutes
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### remoteControl.http\_session

```python
@Metadata.property
def http_session()
```

**Returns**:

- `requests.Session` - HTTP session


### remoteControl.http\_preload

```python
@Metadata.property
def http_preload()
```

**Returns**:

- `bool` - if not streaming


### remoteControl.http\_timeout

```python
@Metadata.property
def http_timeout()
```

**Returns**:

- `int` - HTTP timeout in minutes


### remoteControl.expand

```python
def expand()
```

Expand metadata


## RemoteLoader

```python
class RemoteLoader(Loader)
```

Remote loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.remote import RemoteLoader`


## RemotePlugin

```python
class RemotePlugin(Plugin)
```

Plugin for Remote Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.remote import RemotePlugin`


## Report

```python
class Report(Metadata)
```

Report representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Report`

**Arguments**:

- `descriptor?` _str|dict_ - report descriptor
- `time` _float_ - validation time
- `errors` _Error[]_ - validation errors
- `tasks` _ReportTask[]_ - validation tasks
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### report.version

```python
@property
def version()
```

**Returns**:

- `str` - frictionless version


### report.time

```python
@property
def time()
```

**Returns**:

- `float` - validation time


### report.valid

```python
@property
def valid()
```

**Returns**:

- `bool` - validation result


### report.stats

```python
@property
def stats()
```

**Returns**:

- `dict` - validation stats


### report.errors

```python
@property
def errors()
```

**Returns**:

- `Error[]` - validation errors


### report.tasks

```python
@property
def tasks()
```

**Returns**:

- `ReportTask[]` - validation tasks


### report.task

```python
@property
def task()
```

**Returns**:

- `ReportTask` - validation task (if there is only one)
  

**Raises**:

- `FrictionlessException` - if there are more that 1 task


### report.expand

```python
def expand()
```

Expand metadata


### report.flatten

```python
def flatten(spec=["taskPosition", "rowPosition", "fieldPosition", "code"])
```

Flatten the report

Parameters
spec (any[]): flatten specification

**Returns**:

- `any[]` - flatten report


### report.from\_validate

```python
@staticmethod
def from_validate(validate)
```

Validate function wrapper

**Arguments**:

- `validate` _func_ - validate
  

**Returns**:

- `func` - wrapped validate


## ReportTask

```python
class ReportTask(Metadata)
```

Report task representation.

API      | Usage
-------- | --------
Public   | `from frictionless import ReportTask`

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
- `time` _float_ - validation time
- `scope` _str[]_ - validation scope
- `partial` _bool_ - wehter validation was partial
- `errors` _Error[]_ - validation errors
- `task` _Task_ - validation task
  
  # Raises
- `FrictionlessException` - raise any error that occurs during the process


### reportTask.resource

```python
@property
def resource()
```

**Returns**:

- `Resource` - resource


### reportTask.time

```python
@property
def time()
```

**Returns**:

- `float` - validation time


### reportTask.valid

```python
@property
def valid()
```

**Returns**:

- `bool` - validation result


### reportTask.scope

```python
@property
def scope()
```

**Returns**:

- `str[]` - validation scope


### reportTask.partial

```python
@property
def partial()
```

**Returns**:

- `bool` - if validation partial


### reportTask.stats

```python
@property
def stats()
```

**Returns**:

- `dict` - validation stats


### reportTask.errors

```python
@property
def errors()
```

**Returns**:

- `Error[]` - validation errors


### reportTask.error

```python
@property
def error()
```

**Returns**:

- `Error` - validation error if there is only one
  

**Raises**:

- `FrictionlessException` - if more than one errors


### reportTask.expand

```python
def expand()
```

Expand metadata


### reportTask.flatten

```python
def flatten(spec=["rowPosition", "fieldPosition", "code"])
```

Flatten the report

Parameters
spec (any[]): flatten specification

**Returns**:

- `any[]` - flatten task report


## Resource

```python
class Resource(Metadata)
```

Resource representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Resource`

This class is one of the cornerstones of of Frictionless framework.
It loads a data source, and allows you to stream its parsed contents.
At the same time, it's a metadata class data description.


```python
with Resource("data/table.csv") as resource:
    resource.header == ["id", "name"]
    resource.read_rows() == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]
```

**Arguments**:

  
- `source` _any_ - Source of the resource; can be in various forms.
  Usually, it's a string as `<scheme>://path/to/file.<format>`.
  It also can be, for example, an array of data arrays/dictionaries.
  Or it can be a resource descriptor dict or path.
  
- `descriptor` _dict|str_ - A resource descriptor provided explicitly.
  Keyword arguments will patch this descriptor if provided.
  
- `name?` _str_ - A Resource name according to the specs.
  It should be a slugified name of the resource.
  
- `title?` _str_ - A Resource title according to the specs
  It should a human-oriented title of the resource.
  
- `description?` _str_ - A Resource description according to the specs
  It should a human-oriented description of the resource.
  
- `mediatype?` _str_ - A mediatype/mimetype of the resource e.g. “text/csv”,
  or “application/vnd.ms-excel”.  Mediatypes are maintained by the
  Internet Assigned Numbers Authority (IANA) in a media type registry.
  
- `licenses?` _dict[]_ - The license(s) under which the resource is provided.
  If omitted it's considered the same as the package's licenses.
  
- `sources?` _dict[]_ - The raw sources for this data resource.
  It MUST be an array of Source objects.
  Each Source object MUST have a title and
  MAY have path and/or email properties.
  
- `profile?` _str_ - A string identifying the profile of this descriptor.
  For example, `tabular-data-resource`.
  
- `scheme?` _str_ - Scheme for loading the file (file, http, ...).
  If not set, it'll be inferred from `source`.
  
- `format?` _str_ - File source's format (csv, xls, ...).
  If not set, it'll be inferred from `source`.
  
- `hashing?` _str_ - An algorithm to hash data.
  It defaults to 'md5'.
  
- `encoding?` _str_ - Source encoding.
  If not set, it'll be inferred from `source`.
  
- `innerpath?` _str_ - A path within the compressed file.
  It defaults to the first file in the archive.
  
- `compression?` _str_ - Source file compression (zip, ...).
  If not set, it'll be inferred from `source`.
  
- `control?` _dict|Control_ - File control.
  For more information, please check the Control documentation.
  
- `dialect?` _dict|Dialect_ - Table dialect.
  For more information, please check the Dialect documentation.
  
- `layout?` _dict|Layout_ - Table layout.
  For more information, please check the Layout documentation.
  
- `schema?` _dict|Schema_ - Table schema.
  For more information, please check the Schema documentation.
  
- `stats?` _dict_ - File/table stats.
  A dict with the following possible properties: hash, bytes, fields, rows.
  
- `basepath?` _str_ - A basepath of the resource
  The fullpath of the resource is joined `basepath` and /path`
  
- `detector?` _Detector_ - File/table detector.
  For more information, please check the Detector documentation.
  
- `onerror?` _ignore|warn|raise_ - Behaviour if there is an error.
  It defaults to 'ignore'. The default mode will ignore all errors
  on resource level and they should be handled by the user
  being available in Header and Row objects.
  
- `trusted?` _bool_ - Don't raise an exception on unsafe paths.
  A path provided as a part of the descriptor considered unsafe
  if there are path traversing or the path is absolute.
  A path provided as `source` or `path` is alway trusted.
  
- `package?` _Package_ - A owning this resource package.
  It's actual if the resource is part of some data package.
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### resource.name

```python
@Metadata.property
def name()
```

Returns
    str: resource name


### resource.title

```python
@Metadata.property
def title()
```

Returns
    str: resource title


### resource.description

```python
@Metadata.property
def description()
```

Returns
    str: resource description


### resource.description\_html

```python
@Metadata.property(cache=False, write=False)
def description_html()
```

**Returns**:

- `str?` - resource description


### resource.description\_text

```python
@Metadata.property
def description_text()
```

**Returns**:

- `str` - resource description


### resource.mediatype

```python
@Metadata.property
def mediatype()
```

Returns
    str: resource mediatype


### resource.licenses

```python
@Metadata.property
def licenses()
```

Returns
    dict[]: resource licenses


### resource.sources

```python
@Metadata.property
def sources()
```

Returns
    dict[]: resource sources


### resource.profile

```python
@Metadata.property
def profile()
```

Returns
    str: resource profile


### resource.path

```python
@Metadata.property
def path()
```

Returns
    str: resource path


### resource.data

```python
@Metadata.property
def data()
```

Returns
    any[][]?: resource data


### resource.scheme

```python
@Metadata.property
def scheme()
```

Returns
    str: resource scheme


### resource.format

```python
@Metadata.property
def format()
```

Returns
    str: resource format


### resource.hashing

```python
@Metadata.property
def hashing()
```

Returns
    str: resource hashing


### resource.encoding

```python
@Metadata.property
def encoding()
```

Returns
    str: resource encoding


### resource.innerpath

```python
@Metadata.property
def innerpath()
```

Returns
    str: resource compression path


### resource.compression

```python
@Metadata.property
def compression()
```

Returns
    str: resource compression


### resource.control

```python
@Metadata.property
def control()
```

Returns
    Control: resource control


### resource.dialect

```python
@Metadata.property
def dialect()
```

Returns
    Dialect: resource dialect


### resource.layout

```python
@Metadata.property
def layout()
```

**Returns**:

- `Layout` - table layout


### resource.schema

```python
@Metadata.property
def schema()
```

Returns
    Schema: resource schema


### resource.stats

```python
@Metadata.property
def stats()
```

Returns
    dict: resource stats


### resource.buffer

```python
@property
def buffer()
```

File's bytes used as a sample

These buffer bytes are used to infer characteristics of the
source file (e.g. encoding, ...).

**Returns**:

- `bytes?` - file buffer


### resource.sample

```python
@property
def sample()
```

Table's lists used as sample.

These sample rows are used to infer characteristics of the
source file (e.g. schema, ...).

**Returns**:

- `list[]?` - table sample


### resource.labels

```python
@property
def labels()
```

**Returns**:

- `str[]?` - table labels


### resource.fragment

```python
@property
def fragment()
```

Table's lists used as fragment.

These fragment rows are used internally to infer characteristics of the
source file (e.g. schema, ...).

**Returns**:

- `list[]?` - table fragment


### resource.header

```python
@property
def header()
```

**Returns**:

- `str[]?` - table header


### resource.basepath

```python
@Metadata.property(cache=False, write=False)
def basepath()
```

Returns
    str: resource basepath


### resource.fullpath

```python
@Metadata.property(cache=False, write=False)
def fullpath()
```

Returns
    str: resource fullpath


### resource.detector

```python
@Metadata.property(cache=False, write=False)
def detector()
```

Returns
    str: resource detector


### resource.onerror

```python
@Metadata.property(cache=False, write=False)
def onerror()
```

**Returns**:

- `ignore|warn|raise` - on error bahaviour


### resource.trusted

```python
@Metadata.property(cache=False, write=False)
def trusted()
```

**Returns**:

- `bool` - don't raise an exception on unsafe paths


### resource.package

```python
@Metadata.property(cache=False, write=False)
def package()
```

**Returns**:

- `Package?` - parent package


### resource.tabular

```python
@Metadata.property(write=False)
def tabular()
```

Returns
    bool: if resource is tabular


### resource.byte\_stream

```python
@property
def byte_stream()
```

Byte stream in form of a generator

**Yields**:

- `gen<bytes>?` - byte stream


### resource.text\_stream

```python
@property
def text_stream()
```

Text stream in form of a generator

**Yields**:

- `gen<str[]>?` - text stream


### resource.list\_stream

```python
@property
def list_stream()
```

List stream in form of a generator

**Yields**:

- `gen<any[][]>?` - list stream


### resource.row\_stream

```python
@property
def row_stream()
```

Row stream in form of a generator of Row objects

**Yields**:

- `gen<Row[]>?` - row stream


### resource.expand

```python
def expand()
```

Expand metadata


### resource.infer

```python
def infer(*, stats=False)
```

Infer metadata

**Arguments**:

- `stats?` _bool_ - stream file completely and infer stats


### resource.open

```python
def open()
```

Open the resource as "io.open" does

**Raises**:

- `FrictionlessException` - any exception that occurs


### resource.close

```python
def close()
```

Close the table as "filelike.close" does


### resource.closed

```python
@property
def closed()
```

Whether the table is closed

**Returns**:

- `bool` - if closed


### resource.read\_bytes

```python
def read_bytes(*, size=None)
```

Read bytes into memory

**Returns**:

- `any[][]` - resource bytes


### resource.read\_text

```python
def read_text(*, size=None)
```

Read text into memory

**Returns**:

- `str` - resource text


### resource.read\_data

```python
def read_data(*, size=None)
```

Read data into memory

**Returns**:

- `any` - resource data


### resource.read\_lists

```python
def read_lists(*, size=None)
```

Read lists into memory

**Returns**:

- `any[][]` - table lists


### resource.read\_rows

```python
def read_rows(*, size=None)
```

Read rows into memory

**Returns**:

- `Row[]` - table rows


### resource.write

```python
def write(target=None, **options)
```

Write this resource to the target resource

**Arguments**:

- `target` _any|Resource_ - target or target resource instance
- `**options` _dict_ - Resource constructor options


### resource.to\_dict

```python
def to_dict()
```

Create a dict from the resource

Returns
    dict: dict representation


### resource.to\_copy

```python
def to_copy(**options)
```

Create a copy from the resource

Returns
    Resource: resource copy


### resource.to\_view

```python
def to_view(type="look", **options)
```

Create a view from the resource

See PETL's docs for more information:
https://petl.readthedocs.io/en/stable/util.html#visualising-tables

**Arguments**:

- `type` _look|lookall|see|display|displayall_ - view's type
- `**options` _dict_ - options to be passed to PETL
  
  Returns
- `str` - resource's view


### resource.to\_snap

```python
def to_snap(*, json=False)
```

Create a snapshot from the resource

**Arguments**:

- `json` _bool_ - make data types compatible with JSON format
  
  Returns
- `list` - resource's data


### resource.to\_inline

```python
def to_inline(*, dialect=None)
```

Helper to export resource as an inline data


### resource.to\_pandas

```python
def to_pandas(*, dialect=None)
```

Helper to export resource as an Pandas dataframe


### resource.from\_petl

```python
@staticmethod
def from_petl(view, **options)
```

Create a resource from PETL view


### resource.to\_petl

```python
def to_petl(normalize=False)
```

Export resource as a PETL table


## Row

```python
class Row(dict)
```

Row representation

API      | Usage
-------- | --------
Public   | `from frictionless import Row`

> Constructor of this object is not Public API

This object is returned by `extract`, `resource.read_rows`, and other functions.


```python
rows = extract("data/table.csv")
for row in rows:
    # work with the Row
```

**Arguments**:

- `cells` _any[]_ - array of cells
- `field_info` _dict_ - special field info structure
- `row_position` _int_ - row position from 1
- `row_number` _int_ - row number from 1


### row.cells

```python
@cached_property
def cells()
```

**Returns**:

- `Field[]` - table schema fields


### row.fields

```python
@cached_property
def fields()
```

**Returns**:

- `Field[]` - table schema fields


### row.field\_names

```python
@cached_property
def field_names()
```

**Returns**:

- `Schema` - table schema


### row.field\_positions

```python
@cached_property
def field_positions()
```

**Returns**:

- `int[]` - table field positions


### row.row\_position

```python
@cached_property
def row_position()
```

**Returns**:

- `int` - row position from 1


### row.row\_number

```python
@cached_property
def row_number()
```

**Returns**:

- `int` - row number from 1


### row.blank\_cells

```python
@cached_property
def blank_cells()
```

A mapping indexed by a field name with blank cells before parsing

**Returns**:

- `dict` - row blank cells


### row.error\_cells

```python
@cached_property
def error_cells()
```

A mapping indexed by a field name with error cells before parsing

**Returns**:

- `dict` - row error cells


### row.errors

```python
@cached_property
def errors()
```

**Returns**:

- `Error[]` - row errors


### row.valid

```python
@cached_property
def valid()
```

**Returns**:

- `bool` - if row valid


### row.to\_str

```python
def to_str()
```

**Returns**:

- `str` - a row as a CSV string


### row.to\_list

```python
def to_list(*, json=False, types=None)
```

**Arguments**:

- `json` _bool_ - make data types compatible with JSON format
- `types` _str[]_ - list of supported types
  

**Returns**:

- `dict` - a row as a list


### row.to\_dict

```python
def to_dict(*, json=False, types=None)
```

**Arguments**:

- `json` _bool_ - make data types compatible with JSON format
  

**Returns**:

- `dict` - a row as a dictionary


## S3Control

```python
class S3Control(Control)
```

S3 control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.s3 import S3Control`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `endpoint_url?` _string_ - endpoint url
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### s3Control.expand

```python
def expand()
```

Expand metadata


## S3Loader

```python
class S3Loader(Loader)
```

S3 loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.s3 import S3Loader`


## S3Plugin

```python
class S3Plugin(Plugin)
```

Plugin for S3

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.s3 import S3Plugin`


## Schema

```python
class Schema(Metadata)
```

Schema representation

API      | Usage
-------- | --------
Public   | `from frictionless import Schema`

This class is one of the cornerstones of of Frictionless framework.
It allow to work with Table Schema and its fields.


```python
schema = Schema('schema.json')
schema.add_fied(Field(name='name', type='string'))
```

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
- `fields?` _dict[]_ - list of field descriptors
- `missing_values?` _str[]_ - missing values
- `primary_key?` _str[]_ - primary key
- `foreign_keys?` _dict[]_ - foreign keys
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### schema.missing\_values

```python
@Metadata.property
def missing_values()
```

**Returns**:

- `str[]` - missing values


### schema.primary\_key

```python
@Metadata.property
def primary_key()
```

**Returns**:

- `str[]` - primary key field names


### schema.foreign\_keys

```python
@Metadata.property
def foreign_keys()
```

**Returns**:

- `dict[]` - foreign keys


### schema.fields

```python
@Metadata.property
def fields()
```

**Returns**:

- `Field[]` - an array of field instances


### schema.field\_names

```python
@Metadata.property(cache=False, write=False)
def field_names()
```

**Returns**:

- `str[]` - an array of field names


### schema.add\_field

```python
def add_field(source=None, **options)
```

Add new field to the package.

**Arguments**:

- `source` _dict|str_ - a field source
- `**options` _dict_ - options of the Field class
  

**Returns**:

- `Resource/None` - added `Resource` instance or `None` if not added


### schema.get\_field

```python
def get_field(name)
```

Get schema's field by name.

**Arguments**:

- `name` _str_ - schema field name
  

**Raises**:

- `FrictionlessException` - if field is not found
  

**Returns**:

- `Field` - `Field` instance or `None` if not found


### schema.has\_field

```python
def has_field(name)
```

Check if a field is present

**Arguments**:

- `name` _str_ - schema field name
  

**Returns**:

- `bool` - whether there is the field


### schema.remove\_field

```python
def remove_field(name)
```

Remove field by name.

The schema descriptor will be validated after field descriptor removal.

**Arguments**:

- `name` _str_ - schema field name
  

**Raises**:

- `FrictionlessException` - if field is not found
  

**Returns**:

- `Field/None` - removed `Field` instances or `None` if not found


### schema.expand

```python
def expand()
```

Expand the schema


### schema.read\_cells

```python
def read_cells(cells)
```

Read a list of cells (normalize/cast)

**Arguments**:

- `cells` _any[]_ - list of cells
  

**Returns**:

- `any[]` - list of processed cells


### schema.write\_cells

```python
def write_cells(cells, *, types=[])
```

Write a list of cells (normalize/uncast)

**Arguments**:

- `cells` _any[]_ - list of cells
  

**Returns**:

- `any[]` - list of processed cells


### schema.from\_jsonschema

```python
@staticmethod
def from_jsonschema(profile)
```

Create a Schema from JSONSchema profile

**Arguments**:

- `profile` _str|dict_ - path or dict with JSONSchema profile
  

**Returns**:

- `Schema` - schema instance


## Server

```python
class Server()
```

Server representation

API      | Usage
-------- | --------
Public   | `from frictionless import Schema`


### server.start

```python
def start(port)
```

Start the server

**Arguments**:

- `port` _int_ - HTTP port


### server.stop

```python
def stop()
```

Stop the server


## ServerPlugin

```python
class ServerPlugin(Plugin)
```

Plugin for Server

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.server import ServerPlugin`


## SpssDialect

```python
class SpssDialect(Dialect)
```

Spss dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## SpssParser

```python
class SpssParser(Parser)
```

Spss parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssParser`


## SpssPlugin

```python
class SpssPlugin(Plugin)
```

Plugin for SPSS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssPlugin`


## SqlDialect

```python
class SqlDialect(Dialect)
```

SQL dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `table` _str_ - table name
- `prefix` _str_ - prefix for all table names
- `order_by?` _str_ - order_by statement passed to SQL
- `where?` _str_ - where statement passed to SQL
- `namespace?` _str_ - SQL schema
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## SqlParser

```python
class SqlParser(Parser)
```

SQL parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlParser`


## SqlPlugin

```python
class SqlPlugin(Plugin)
```

Plugin for SQL

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlPlugin`


## SqlStorage

```python
class SqlStorage(Storage)
```

SQL storage implementation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlStorage`

**Arguments**:

- `url?` _string_ - SQL connection string
- `engine?` _object_ - `sqlalchemy` engine
- `prefix?` _str_ - prefix for all tables
- `namespace?` _str_ - SQL scheme


## Status

```python
class Status(Metadata)
```

Status representation.

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### status.version

```python
@property
def version()
```

**Returns**:

- `str` - frictionless version


### status.time

```python
@property
def time()
```

**Returns**:

- `float` - transformation time


### status.valid

```python
@property
def valid()
```

**Returns**:

- `bool` - transformation result


### status.stats

```python
@property
def stats()
```

**Returns**:

- `dict` - transformation stats


### status.errors

```python
@property
def errors()
```

**Returns**:

- `Error[]` - transformation errors


### status.tasks

```python
@property
def tasks()
```

**Returns**:

- `ReportTable[]` - transformation tasks


### status.task

```python
@property
def task()
```

**Returns**:

- `ReportTable` - transformation task (if there is only one)
  

**Raises**:

- `FrictionlessException` - if there are more that 1 task


## StatusTask

```python
class StatusTask(Metadata)
```

Status Task representation


### statusTask.time

```python
@property
def time()
```

**Returns**:

- `dict` - transformation time


### statusTask.valid

```python
@property
def valid()
```

**Returns**:

- `bool` - transformation result


### statusTask.stats

```python
@property
def stats()
```

**Returns**:

- `dict` - transformation stats


### statusTask.errors

```python
@property
def errors()
```

**Returns**:

- `Error[]` - transformation errors


### statusTask.target

```python
@property
def target()
```

**Returns**:

- `any` - transformation target


### statusTask.type

```python
@property
def type()
```

**Returns**:

- `any` - transformation target


## Step

```python
class Step(Metadata)
```

Step representation


### step.transform\_resource

```python
def transform_resource(resource)
```

Transform resource

**Arguments**:

- `resource` _Resource_ - resource
  

**Returns**:

- `resource` _Resource_ - resource


### step.transform\_package

```python
def transform_package(resource)
```

Transform package

**Arguments**:

- `package` _Package_ - package
  

**Returns**:

- `package` _Package_ - package


## StreamControl

```python
class StreamControl(Control)
```

Stream control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.stream import StreamControl`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## StreamLoader

```python
class StreamLoader(Loader)
```

Stream loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.stream import StreamLoader`


## StreamPlugin

```python
class StreamPlugin(Plugin)
```

Plugin for Local Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.stream import StreamPlugin`


## System

```python
class System()
```

System representation

API      | Usage
-------- | --------
Public   | `from frictionless import system`

This class provides an ability to make system Frictionless calls.
It's available as `frictionless.system` singletone.


### system.register

```python
def register(name, plugin)
```

Register a plugin

**Arguments**:

- `name` _str_ - plugin name
- `plugin` _Plugin_ - plugin to register


### system.deregister

```python
def deregister(name)
```

Deregister a plugin

**Arguments**:

- `name` _str_ - plugin name


### system.create\_candidates

```python
def create_candidates()
```

Create candidates

**Returns**:

- `dict[]` - an ordered by priority list of type descriptors for type detection


### system.create\_check

```python
def create_check(descriptor)
```

Create check

**Arguments**:

- `descriptor` _dict_ - check descriptor
  

**Returns**:

- `Check` - check


### system.create\_control

```python
def create_control(resource, *, descriptor)
```

Create control

**Arguments**:

- `resource` _Resource_ - control resource
- `descriptor` _dict_ - control descriptor
  

**Returns**:

- `Control` - control


### system.create\_dialect

```python
def create_dialect(resource, *, descriptor)
```

Create dialect

**Arguments**:

- `resource` _Resource_ - dialect resource
- `descriptor` _dict_ - dialect descriptor
  

**Returns**:

- `Dialect` - dialect


### system.create\_error

```python
def create_error(descriptor)
```

Create error

**Arguments**:

- `descriptor` _dict_ - error descriptor
  

**Returns**:

- `Error` - error


### system.create\_file

```python
def create_file(source, **options)
```

Create file

**Arguments**:

- `source` _any_ - file source
- `options` _dict_ - file options
  

**Returns**:

- `File` - file


### system.create\_loader

```python
def create_loader(resource)
```

Create loader

**Arguments**:

- `resource` _Resource_ - loader resource
  

**Returns**:

- `Loader` - loader


### system.create\_parser

```python
def create_parser(resource)
```

Create parser

**Arguments**:

- `resource` _Resource_ - parser resource
  

**Returns**:

- `Parser` - parser


### system.create\_server

```python
def create_server(name, **options)
```

Create server

**Arguments**:

- `name` _str_ - server name
- `options` _str_ - server options
  

**Returns**:

- `Server` - server


### system.create\_step

```python
def create_step(descriptor)
```

Create step

**Arguments**:

- `descriptor` _dict_ - step descriptor
  

**Returns**:

- `Step` - step


### system.create\_storage

```python
def create_storage(name, source, **options)
```

Create storage

**Arguments**:

- `name` _str_ - storage name
- `options` _str_ - storage options
  

**Returns**:

- `Storage` - storage


### system.create\_type

```python
def create_type(field)
```

Create type

**Arguments**:

- `field` _Field_ - corresponding field
  

**Returns**:

- `Type` - type


### system.get\_http\_session

```python
def get_http_session()
```

Return a HTTP session

This method will return a new session or the session
from `system.use_http_session` context manager

**Returns**:

- `requests.Session` - a HTTP session


### system.use\_http\_session

```python
@contextmanager
def use_http_session(http_session=None)
```

HTTP session context manager


```
session = requests.Session(...)
with system.use_http_session(session):
    # work with frictionless using a user defined HTTP session
    report = validate(...)
```

**Arguments**:

- `http_session?` _requests.Session_ - a session; will create a new if omitted


## Type

```python
class Type()
```

Data type representation

API      | Usage
-------- | --------
Public   | `from frictionless import Type`

This class is for subclassing.

**Arguments**:

- `field` _Field_ - field


### type.constraints

**Returns**:

- `str[]` - a list of supported constraints


### type.field

```python
@cached_property
def field()
```

**Returns**:

- `Field` - field


### type.read\_cell

```python
def read_cell(cell)
```

Convert cell (read direction)

**Arguments**:

- `cell` _any_ - cell to covert
  

**Returns**:

- `any` - converted cell


### type.write\_cell

```python
def write_cell(cell)
```

Convert cell (write direction)

**Arguments**:

- `cell` _any_ - cell to covert
  

**Returns**:

- `any` - converted cell


## XlsParser

```python
class XlsParser(Parser)
```

XLS parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import XlsParser


## XlsxParser

```python
class XlsxParser(Parser)
```

XLSX parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import XlsxParser


## checks.baseline

```python
class baseline(Check)
```

Check a table for basic errors

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(...)`

Ths check is enabled by default for any `validate` function run.


## checks.deviated\_value

```python
class deviated_value(Check)
```

Check for deviated values in a field

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checks=([{"code": "deviated-value", **descriptor}])`

This check can be enabled using the `checks` parameter
for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `field_name` _str_ - a field name to check
- `average?` _str_ - one of "mean", "median" or "mode" (default: "mean")
- `interval?` _str_ - statistical interval (default: 3)


## checks.duplicate\_row

```python
class duplicate_row(Check)
```

Check for duplicate rows

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checks=[{"code": "duplicate-row"}])`

This check can be enabled using the `checks` parameter
for the `validate` function.


## checks.forbidden\_value

```python
class forbidden_value(Check)
```

Check for forbidden values in a field

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checks=[{"code": "backlisted-value", **descriptor}])`

This check can be enabled using the `checks` parameter
for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `field_name` _str_ - a field name to look into
- `forbidden` _any[]_ - a list of forbidden values


## checks.row\_constraint

```python
class row_constraint(Check)
```

Check that every row satisfies a provided Python expression

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checks=([{"code": "row-constraint", **descriptor}])`

This check can be enabled using the `checks` parameter
for the `validate` function. The syntax for the row constraint
check can be found here - https://github.com/danthedeckie/simpleeval

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `formula` _str_ - a python expression to evaluate against a row


## checks.sequential\_value

```python
class sequential_value(Check)
```

Check that a column having sequential values

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checks=[{"code": "sequential-value", **descriptor}])`

This check can be enabled using the `checks` parameter
for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `field_name` _str_ - a field name to check


## checks.truncated\_value

```python
class truncated_value(Check)
```

Check for possible truncated values

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checks=([{"code": "truncated-value"}])`

This check can be enabled using the `checks` parameter
for the `validate` function.


## describe

```python
def describe(source=None, *, type=None, **options)
```

Describe the data source

API      | Usage
-------- | --------
Public   | `from frictionless import describe`

**Arguments**:

- `source` _any_ - data source
- `type` _str_ - source type - `schema`, `resource` or `package` (default: infer)
- `**options` _dict_ - options for the underlaying describe function
  

**Returns**:

- `Package|Resource|Schema` - metadata


## describe\_dialect

```python
def describe_dialect(source=None, **options)
```

Describe the given source as a dialect

API      | Usage
-------- | --------
Public   | `from frictionless import describe_dialect`

**Arguments**:

- `source` _any_ - data source
- `**options` _dict_ - describe resource options
  

**Returns**:

- `Dialect` - file dialect


## describe\_package

```python
def describe_package(source=None, *, expand=False, stats=False, **options)
```

Describe the given source as a package

API      | Usage
-------- | --------
Public   | `from frictionless import describe_package`

**Arguments**:

- `source` _any_ - data source
- `expand?` _bool_ - if `True` it will expand the metadata
- `stats?` _bool_ - if `True` infer resource's stats
- `**options` _dict_ - Package constructor options
  

**Returns**:

- `Package` - data package


## describe\_resource

```python
def describe_resource(source=None, *, expand=False, stats=False, **options)
```

Describe the given source as a resource

API      | Usage
-------- | --------
Public   | `from frictionless import describe_resource`

**Arguments**:

- `source` _any_ - data source
- `expand?` _bool_ - if `True` it will expand the metadata
- `stats?` _bool_ - if `True` infer resource's stats
- `**options` _dict_ - Resource constructor options
  

**Returns**:

- `Resource` - data resource


## describe\_schema

```python
def describe_schema(source=None, **options)
```

Describe the given source as a schema

API      | Usage
-------- | --------
Public   | `from frictionless import describe_schema`

**Arguments**:

- `source` _any_ - data source
- `**options` _dict_ - describe resource options
  

**Returns**:

- `Schema` - table schema


## errors.CellError

```python
class CellError(RowError)
```

Cell error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `cells` _str[]_ - row cells
- `row_number` _int_ - row number
- `row_position` _int_ - row position
- `cell` _str_ - errored cell
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  
  # Raises
- `FrictionlessException` - raise any error that occurs during the process


### errors.CellError.from\_row

```python
@classmethod
def from_row(cls, row, *, note, field_name)
```

Create and error from a cell

**Arguments**:

- `row` _Row_ - row
- `note` _str_ - note
- `field_name` _str_ - field name
  

**Returns**:

- `CellError` - error


## errors.HeaderError

```python
class HeaderError(TableError)
```

Header error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `labels` _str[]_ - header labels
- `label` _str_ - an errored label
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## errors.LabelError

```python
class LabelError(HeaderError)
```

Label error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `labels` _str[]_ - header labels
- `label` _str_ - an errored label
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


## errors.RowError

```python
class RowError(TableError)
```

Row error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `row_number` _int_ - row number
- `row_position` _int_ - row position
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process


### errors.RowError.from\_row

```python
@classmethod
def from_row(cls, row, *, note)
```

Create an error from a row

**Arguments**:

- `row` _Row_ - row
- `note` _str_ - note
  

**Returns**:

- `RowError` - error


## extract

```python
def extract(source=None, *, type=None, process=None, stream=False, **options)
```

Extract resource rows

API      | Usage
-------- | --------
Public   | `from frictionless import extract`

**Arguments**:

- `source` _dict|str_ - data source
- `type` _str_ - source type - package of resource (default: infer)
- `process?` _func_ - a row processor function
- `stream?` _bool_ - return a row stream(s) instead of loading into memory
- `**options` _dict_ - options for the underlaying function
  

**Returns**:

- `Row[]|{path` - Row[]}: rows in a form depending on the source type


## extract\_package

```python
def extract_package(source=None, *, process=None, stream=False, **options)
```

Extract package rows

API      | Usage
-------- | --------
Public   | `from frictionless import extract_package`

**Arguments**:

- `source` _dict|str_ - data resource descriptor
- `process?` _func_ - a row processor function
- `stream?` _bool_ - return a row streams instead of loading into memory
- `**options` _dict_ - Package constructor options
  

**Returns**:

- `{path` - Row[]}: a dictionary of arrays/streams of rows


## extract\_resource

```python
def extract_resource(source=None, *, process=None, stream=False, **options)
```

Extract resource rows

API      | Usage
-------- | --------
Public   | `from frictionless import extract_resource`

**Arguments**:

- `source` _any|Resource_ - data resource
- `process?` _func_ - a row processor function
- `**options` _dict_ - Resource constructor options
  

**Returns**:

- `Row[]` - an array/stream of rows


## steps.cell\_convert

```python
class cell_convert(Step)
```

Convert cell


## steps.cell\_fill

```python
class cell_fill(Step)
```

Fill cell


## steps.cell\_format

```python
class cell_format(Step)
```

Format cell


## steps.cell\_interpolate

```python
class cell_interpolate(Step)
```

Interpolate cell


## steps.cell\_replace

```python
class cell_replace(Step)
```

Replace cell


## steps.cell\_set

```python
class cell_set(Step)
```

Set cell


## steps.field\_add

```python
class field_add(Step)
```

Add field


## steps.field\_filter

```python
class field_filter(Step)
```

Filter fields


## steps.field\_move

```python
class field_move(Step)
```

Move field


## steps.field\_remove

```python
class field_remove(Step)
```

Remove field


## steps.field\_split

```python
class field_split(Step)
```

Split field


## steps.field\_unpack

```python
class field_unpack(Step)
```

Unpack field


## steps.field\_update

```python
class field_update(Step)
```

Update field


## steps.resource\_add

```python
class resource_add(Step)
```

Add resource


## steps.resource\_remove

```python
class resource_remove(Step)
```

Remove resource


## steps.resource\_transform

```python
class resource_transform(Step)
```

Transform resource


## steps.resource\_update

```python
class resource_update(Step)
```

Update resource


## steps.row\_filter

```python
class row_filter(Step)
```

Filter rows


## steps.row\_search

```python
class row_search(Step)
```

Search rows


## steps.row\_slice

```python
class row_slice(Step)
```

Slice rows


## steps.row\_sort

```python
class row_sort(Step)
```

Sort rows


## steps.row\_split

```python
class row_split(Step)
```

Split rows


## steps.row\_subset

```python
class row_subset(Step)
```

Subset rows


## steps.row\_ungroup

```python
class row_ungroup(Step)
```

Ungroup rows


## steps.table\_aggregate

```python
class table_aggregate(Step)
```

Aggregate table


## steps.table\_attach

```python
class table_attach(Step)
```

Attach table


## steps.table\_debug

```python
class table_debug(Step)
```

Debug table


## steps.table\_diff

```python
class table_diff(Step)
```

Diff tables


## steps.table\_intersect

```python
class table_intersect(Step)
```

Intersect tables


## steps.table\_join

```python
class table_join(Step)
```

Join tables


## steps.table\_melt

```python
class table_melt(Step)
```

Melt tables


## steps.table\_merge

```python
class table_merge(Step)
```

Merge tables


## steps.table\_normalize

```python
class table_normalize(Step)
```

Normalize table


## steps.table\_pivot

```python
class table_pivot(Step)
```

Pivot table


## steps.table\_print

```python
class table_print(Step)
```

Print table


## steps.table\_recast

```python
class table_recast(Step)
```

Recast table


## steps.table\_transpose

```python
class table_transpose(Step)
```

Transpose table


## steps.table\_validate

```python
class table_validate(Step)
```

Validate table


## steps.table\_write

```python
class table_write(Step)
```

Write table


## transform

```python
def transform(source=None, type=None, **options)
```

Transform resource

API      | Usage
-------- | --------
Public   | `from frictionless import transform`

**Arguments**:

- `source` _any_ - data source
- `type` _str_ - source type - package, resource or pipeline (default: infer)
- `**options` _dict_ - options for the underlaying function
  

**Returns**:

- `any` - the transform result


## transform\_package

```python
def transform_package(source=None, *, steps, **options)
```

Transform package

API      | Usage
-------- | --------
Public   | `from frictionless import transform_package`

**Arguments**:

- `source` _any_ - data source
- `steps` _Step[]_ - transform steps
- `**options` _dict_ - Package constructor options
  

**Returns**:

- `Package` - the transform result


## transform\_pipeline

```python
def transform_pipeline(source=None, *, parallel=False, **options)
```

Transform package

API      | Usage
-------- | --------
Public   | `from frictionless import transform_package`

**Arguments**:

- `source` _any_ - a pipeline descriptor
- `**options` _dict_ - Pipeline constructor options
  

**Returns**:

- `any` - the pipeline output


## transform\_resource

```python
def transform_resource(source=None, *, steps, **options)
```

Transform resource

API      | Usage
-------- | --------
Public   | `from frictionless import transform_resource`

**Arguments**:

- `source` _any_ - data source
- `steps` _Step[]_ - transform steps
- `**options` _dict_ - Package constructor options
  

**Returns**:

- `Resource` - the transform result


## types.AnyType

```python
class AnyType(Type)
```

Any type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.ArrayType

```python
class ArrayType(Type)
```

Array type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.BooleanType

```python
class BooleanType(Type)
```

Boolean type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.DateType

```python
class DateType(Type)
```

Date type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.DatetimeType

```python
class DatetimeType(Type)
```

Datetime type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.DurationType

```python
class DurationType(Type)
```

Duration type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.GeojsonType

```python
class GeojsonType(Type)
```

Geojson type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.GeopointType

```python
class GeopointType(Type)
```

Geopoint type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.IntegerType

```python
class IntegerType(Type)
```

Integer type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.NumberType

```python
class NumberType(Type)
```

Number type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.ObjectType

```python
class ObjectType(Type)
```

Object type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.StringType

```python
class StringType(Type)
```

String type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.TimeType

```python
class TimeType(Type)
```

Time type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.YearType

```python
class YearType(Type)
```

Year type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## types.YearmonthType

```python
class YearmonthType(Type)
```

Yearmonth type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`


## validate

```python
@Report.from_validate
def validate(source=None, type=None, **options)
```

Validate resource

API      | Usage
-------- | --------
Public   | `from frictionless import validate`

**Arguments**:

- `source` _dict|str_ - a data source
- `type` _str_ - source type - inquiry, package, resource, schema or table
- `**options` _dict_ - options for the underlaying function
  

**Returns**:

- `Report` - validation report


## validate\_inquiry

```python
@Report.from_validate
def validate_inquiry(source=None, *, parallel=False, **options)
```

Validate inquiry

API      | Usage
-------- | --------
Public   | `from frictionless import validate_inquiry`

**Arguments**:

- `source` _dict|str_ - an inquiry descriptor
- `parallel?` _bool_ - enable multiprocessing
  

**Returns**:

- `Report` - validation report


## validate\_package

```python
@Report.from_validate
def validate_package(source=None, original=False, parallel=False, **options)
```

Validate package

API      | Usage
-------- | --------
Public   | `from frictionless import validate_package`

**Arguments**:

- `source` _dict|str_ - a package descriptor
- `basepath?` _str_ - package basepath
- `trusted?` _bool_ - don't raise an exception on unsafe paths
- `original?` _bool_ - don't call `package.infer`
- `parallel?` _bool_ - enable multiprocessing
- `**options` _dict_ - Package constructor options
  

**Returns**:

- `Report` - validation report


## validate\_resource

```python
@Report.from_validate
def validate_resource(source=None, *, checks=None, original=False, pick_errors=None, skip_errors=None, limit_errors=settings.DEFAULT_LIMIT_ERRORS, limit_memory=settings.DEFAULT_LIMIT_MEMORY, **options, ,)
```

Validate table

API      | Usage
-------- | --------
Public   | `from frictionless import validate_table`

**Arguments**:

- `source` _any_ - the source of the resource
- `checks?` _list_ - a list of checks
  pick_errors? ((str|int)[]): pick errors
  skip_errors? ((str|int)[]): skip errors
- `limit_errors?` _int_ - limit errors
- `limit_memory?` _int_ - limit memory
- `original?` _bool_ - validate resource as it is
- `**options?` _dict_ - Resource constructor options
  

**Returns**:

- `Report` - validation report

## validate\_schema

```python
@Report.from_validate
def validate_schema(source=None, **options)
```

Validate schema

API      | Usage
-------- | --------
Public   | `from frictionless import validate_schema`

**Arguments**:

- `source` _dict|str_ - a schema descriptor
  

**Returns**:

- `Report` - validation report


