---
title: Resource Guide
---

> This guide in under development. We are moving some shared Resource information from describe, extract, validate, and transform guides to this guide.

## Exploring Data

There are various functions to help explore your resource, such as checking a header or other attributes like stats:


```python
from frictionless import Resource

with Resource('tmp/country.resource.json', basepath='.') as resource:
    print(f'Source: "{resource.source}"')
    print(f'Scheme: "{resource.scheme}"')
    print(f'Format: "{resource.format}"')
    print(f'Hashing: "{resource.hashing}"')
    print(f'Encoding: "{resource.encoding}"')
    print(f'Innerpaath: "{resource.innerpath}"')
    print(f'Compression: "{resource.compression}"')
    pprint(resource.read_header())
    pprint(resource.read_sample())
    pprint(resource.read_stats())
```

    Source: "data/capital-3.csv"
    Scheme: "file"
    Format: "csv"
    Hashing: "md5"
    Encoding: "utf-8"
    Innerpath: ""
    Compression: ""
    ['id', 'capital_id', 'name', 'population']
    [['1', '1', 'Britain', '67'],
     ['2', '3', 'France', '67'],
     ['3', '2', 'Germany', '83'],
     ['4', '5', 'Italy', '60'],
     ['5', '4', 'Spain', '47']]
    {'bytes': 100,
     'fields': 4,
     'hash': 'c0558b91523683483f86f63346d06d81',
     'rows': 5}

There is much more information available; we will explain some of it later in the sections below:


```python
from frictionless import Table

with Resource('data/capital-3.csv') as resource:
  print(f'Control: "{resource.control}"')
  print(f'Dialect: "{resource.dialect}"')
  print(f'Layout: "{resource.layout}"')
  print(f'Schema: "{resource.schema}"')
  print(f'Stats: "{resource.stats}"')
  print(f'Fragment: "{resource.fragment}"')
  print(f'Header: "{resource.header}"')
```

```
Control: "{}"
Dialect: "{}"
Layout: "{}"
Schema: "{'fields': [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]}"
Stats: "{'hash': 'e7b6592a0a4356ba834e4bf1c8e8c7f8', 'bytes': 50, 'fields': 2, 'rows': 0}"
Fragment: "[['1', 'London'], ['2', 'Berlin'], ['3', 'Paris'], ['4', 'Madrid'], ['5', 'Rome']]"
Header: "['id', 'name']"
```

Many of the properties above not only can be read from the existent Table but also can be provided as an option to alter the Table behaviour, for example:

## Table's Lifecycle

You might have noticed that we had to duplicate the `with Table(...)` statement in some examples. The reason is that Table is a streaming interface. Once it's read you need to open it again. Let's show it in an example:


```python
from frictionless import Table

table = Table('data/capital-3.csv')
table.open()
pprint(table.read_rows())
pprint(table.read_rows())
# We need to re-open: there is no data left
table.open()
pprint(table.read_rows())
# We need to close manually: not context manager is used
table.close()
```

    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', 3), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]
    []
    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', 3), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]


## File Details

Let's overview the details we can specify for a file. Usually you don't need to provide those details as Frictionless is capable to infer it on its own. Although, there are situation when you need to specify it manually. The following example will use the `Table` class but the same options can be used for the `extract` and `extract_table` functions.

### Scheme

The scheme also know as protocol indicates which loader Frictionless should use to read or write data. It can be `file` (default), `text`, `http`, `https`, `s3`, and others.


```python
from frictionless import Table

with Table('header1,header2\nvalue1,value2.csv', scheme='text') as table:
  print(table.scheme)
  print(table.read_rows())
```

    text
    [Row([('header1', 'value1'), ('header2', 'value2.csv')])]


### Format

The format or as it's also called extension helps Frictionless to choose a proper parser to handle the file. Popular formats are `csv`, `xlsx`, `json` and others


```python
from frictionless import Table

with Table('text://header1,header2\nvalue1,value2.csv', format='csv') as table:
  print(table.format)
  print(table.read_rows())
```

    csv
    [Row([('header1', 'value1'), ('header2', 'value2')])]


### Hashing

The hashing option controls which hashing algorithm should be used for generating the `hash` property. It doesn't affect the `extract` function but can be used with the `Table` class:


```python
from frictionless import Table

with Table('data/country-3.csv', hashing='sha256') as table:
  table.read_rows()
  print(table.hashing)
  print(table.stats['hash'])
```

    sha256
    408b5058f961915c1e1f3bc318ab01d7d094a4daccdf03ad6022cfc7b8ea4e3e


### Encoding

Frictionless automatically detects encoding of files but sometimes it can be inaccurate. It's possible to provide an encoding manually:


```python
from frictionless import Table

with Table('data/country-3.csv', encoding='utf-8') as table:
  print(table.encoding)
  print(table.source)
```

    utf-8
    data/country-3.csv


### Compression

It's possible to adjust compression detection by providing the algorithm explicitly. For the example below it's not required as it would be detected anyway:


```python
from frictionless import Table

with Table('data/table.csv.zip', compression='zip') as table:
  print(table.compression)
  print(table.read_rows())
```

    zip
    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


### Compression Path

By default, Frictionless uses the first file found in a zip archive. It's possible to adjust this behaviour:


```python
from frictionless import Table

with Table('data/table-multiple-files.zip', compression_path='table-reverse.csv') as table:
  print(table.compression)
  print(table.compression_path)
  print(table.read_rows())
```

    zip
    table-reverse.csv
    [Row([('id', 1), ('name', '中国人')]), Row([('id', 2), ('name', 'english')])]


Further reading:
- Schemes Reference
- Formats Reference

## File Control

The Control object allows you to manage the loader used by the Table class. In most cases, you don't need to provide any Control settings but sometimes it can be useful:


```python
from frictionless import Table
from frictionless.plugins.remote import RemoteControl

source = 'https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv'
control = RemoteControl(http_timeout=10)
with Table(source, control=control) as table:
  print(table.control)
  print(table.read_rows())
```

    {'httpTimeout': 10, 'newline': ''}
    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


Exact parameters depend on schemes and can be found in the "Schemes Reference". For example, the Remote Control provides `http_timeout`, `http_session`, and others but there is only one option available for all controls:

### Detect Encoding

It's a function that can be provided to adjust the encoding detection. This function accepts a data sample and returns a detected encoding:


```python
from frictionless import Table, Control

control = Control(detect_encoding=lambda sample: "utf-8")
with Table("data/capital-3.csv", control=control) as table:
  print(table.source)
  print(table.encoding)
```

    data/capital-3.csv
    utf-8


Further reading:
- Schemes Reference

## Table Dialect

The Dialect adjusts the way tabular parsers work. The concept is similar to the Control above. Let's use the CSV Dialect to adjust the delimiter configuration:


```python
from frictionless import Table
from frictionless.plugins.csv import CsvDialect

source = 'header1;header2\nvalue1;value2'
dialect = CsvDialect(delimiter=';')
with Table(source, scheme='text', format='csv', dialect=dialect) as table:
  print(table.dialect)
  print(table.read_rows())
```

    {'delimiter': ';'}
    [Row([('header1', 'value1'), ('header2', 'value2')])]


There are a great deal of options available for different dialects that can be found in "Formats Reference". We will list the properties that can be used with every dialect:

### Header

It's a boolean flag which defaults to `True` indicating whether the data has a header row or not. In the following example the header row will be treated as a data row:


```python
from frictionless import Table, Dialect

dialect = Dialect(header=False)
with Table('data/capital-3.csv', dialect=dialect) as table:
  pprint(table.header)
  pprint(table.read_rows())
```

    []
    [Row([('field1', 'id'), ('field2', 'name')]),
     Row([('field1', '1'), ('field2', 'London')]),
     Row([('field1', '2'), ('field2', 'Berlin')]),
     Row([('field1', '3'), ('field2', 'Paris')]),
     Row([('field1', '4'), ('field2', 'Madrid')]),
     Row([('field1', '5'), ('field2', 'Rome')])]


### Header Rows

If header is `True` which is default, this parameters indicates where to find the header row or header rows for a multiline header. Let's see on example how the first two data rows can be treated as a part of a header:


```python
from frictionless import Table, Dialect

dialect = Dialect(header_rows=[1, 2, 3])
with Table('data/capital-3.csv', dialect=dialect) as table:
  pprint(table.header)
  pprint(table.read_rows())
```

    ['id 1 2', 'name London Berlin']
    [Row([('id 1 2', 3), ('name London Berlin', 'Paris')]),
     Row([('id 1 2', 4), ('name London Berlin', 'Madrid')]),
     Row([('id 1 2', 5), ('name London Berlin', 'Rome')])]


### Header Join

If there are multiple header rows which is managed by `header_rows` parameter, we can set a string to be a separator for a header's cell join operation. Usually it's very handy for some "fancy" Excel files. For the sake of simplicity, we will show on a CSV file:


```python
from frictionless import Table, Dialect

dialect = Dialect(header_rows=[1, 2, 3], header_join='/')
with Table('data/capital-3.csv', dialect=dialect) as table:
  pprint(table.header)
  pprint(table.read_rows())
```

    ['id/1/2', 'name/London/Berlin']
    [Row([('id/1/2', 3), ('name/London/Berlin', 'Paris')]),
     Row([('id/1/2', 4), ('name/London/Berlin', 'Madrid')]),
     Row([('id/1/2', 5), ('name/London/Berlin', 'Rome')])]


### Header Case

> *New in version 3.23*

By default a header is validated in a case sensitive mode. To disable this behaviour we can set the `header_case` parameter to `False`. This option is accepted by any Dialect and a dialect can be passed to `extract`, `validate` and other functions. Please note that it doesn't affect a resulting header it only affects how it's validated:


```python
from frictionless import Table, Schema, Field, Dialect

dialect = Dialect(header_case=False)
schema = Schema(fields=[Field(name="ID"), Field(name="NAME")])
with Table('data/capital-3.csv', dialect=dialect, schema=schema) as table:
  print(f'Header: {table.header}')
  print(f'Valid: {table.header.valid}')  # without "header_case" it will have 2 errors
```

    Header: ['id', 'name']
    Valid: True


Further reading:
- Formats Reference

## Table Query

Using header management described in the "Table Dialect" section we can have a basic skipping rows ability e.g. if we set `dialect.header_rows=[2]` we will skip the first row but it's very limited. There is a much more powerful interface called Table Queries to indicate where exactly to get tabular data from a file. We will use a simple file looking like a matrix:


```python
! cat data/matrix.csv
```

    f1,f2,f3,f4
    11,12,13,14
    21,22,23,24
    31,32,33,34
    41,42,43,44


### Pick/Skip Fields

We can pick and skip arbitrary fields based on a header row. These options accept a list of field numbers, a list of strings or a regex to match. All the queries below do the same thing for this file:


```python
from frictionless import extract, Query

print(extract('data/matrix.csv', query=Query(pick_fields=[2, 3])))
print(extract('data/matrix.csv', query=Query(skip_fields=[1, 4])))
print(extract('data/matrix.csv', query=Query(pick_fields=['f2', 'f3'])))
print(extract('data/matrix.csv', query=Query(skip_fields=['f1', 'f4'])))
print(extract('data/matrix.csv', query=Query(pick_fields=['<regex>f[23]'])))
print(extract('data/matrix.csv', query=Query(skip_fields=['<regex>f[14]'])))
```

    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]


### Limit/Offset Fields

There are two options that provide an ability to limit amount of fields similar to SQL's directives:


```python
from frictionless import extract, Query

print(extract('data/matrix.csv', query=Query(limit_fields=2)))
print(extract('data/matrix.csv', query=Query(offset_fields=2)))
```

    [Row([('f1', 11), ('f2', 12)]), Row([('f1', 21), ('f2', 22)]), Row([('f1', 31), ('f2', 32)]), Row([('f1', 41), ('f2', 42)])]
    [Row([('f3', 13), ('f4', 14)]), Row([('f3', 23), ('f4', 24)]), Row([('f3', 33), ('f4', 34)]), Row([('f3', 43), ('f4', 44)])]


### Pick/Skip Rows

It's alike the field counterparts but it will be compared to the first cell of a row. All the queries below do the same thing for this file but take into account that when picking we need to also pick a header row. In addition, there is special value `<blank>` that matches a row if it's completely blank:


```python
from frictionless import extract, Query

print(extract('data/matrix.csv', query=Query(pick_rows=[1, 3, 4])))
print(extract('data/matrix.csv', query=Query(skip_rows=[2, 5])))
print(extract('data/matrix.csv', query=Query(pick_rows=['f1', '21', '31'])))
print(extract('data/matrix.csv', query=Query(skip_rows=['11', '41'])))
print(extract('data/matrix.csv', query=Query(pick_rows=['<regex>(f1|[23]1)'])))
print(extract('data/matrix.csv', query=Query(skip_rows=['<regex>[14]1'])))
print(extract('data/matrix.csv', query=Query(pick_rows=['<blank>'])))
```

    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    []


### Limit/Offset Rows

This is a quite popular option used to limit amount of rows to read:


```python
from frictionless import extract, Query

print(extract('data/matrix.csv', query=Query(limit_rows=2)))
print(extract('data/matrix.csv', query=Query(offset_rows=2)))
```

    [Row([('f1', 11), ('f2', 12), ('f3', 13), ('f4', 14)]), Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)])]
    [Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)]), Row([('f1', 41), ('f2', 42), ('f3', 43), ('f4', 44)])]


## Header Options

Header management is a responsibility of "Table Dialect" which will be described below but Table accept a special `headers` argument that plays a role of a high-level helper in setting different header options.

It accepts a `False` values indicating that there is no header row:


```python
from frictionless import Table

with Table('data/capital-3.csv', headers=False) as table:
    pprint(table.header)
    pprint(table.read_rows())
```

    []
    [Row([('field1', 'id'), ('field2', 'name')]),
     Row([('field1', '1'), ('field2', 'London')]),
     Row([('field1', '2'), ('field2', 'Berlin')]),
     Row([('field1', '3'), ('field2', 'Paris')]),
     Row([('field1', '4'), ('field2', 'Madrid')]),
     Row([('field1', '5'), ('field2', 'Rome')])]


It accepts an integer indicating the header row number:


```python
from frictionless import Table

with Table('data/capital-3.csv', headers=2) as table:
    pprint(table.header)
    pprint(table.read_rows())
```

    ['1', 'London']
    [Row([('1', 2), ('London', 'Berlin')]),
     Row([('1', 3), ('London', 'Paris')]),
     Row([('1', 4), ('London', 'Madrid')]),
     Row([('1', 5), ('London', 'Rome')])]


It accepts a list of integers indicating a multiline header row numbers:


```python
from frictionless import Table

with Table('data/capital-3.csv', headers=[1,2,3]) as table:
    pprint(table.header)
    pprint(table.read_rows())
```

    ['id 1 2', 'name London Berlin']
    [Row([('id 1 2', 3), ('name London Berlin', 'Paris')]),
     Row([('id 1 2', 4), ('name London Berlin', 'Madrid')]),
     Row([('id 1 2', 5), ('name London Berlin', 'Rome')])]


It accepts a pair containing a list of integers indicating a multiline header row numbers and a string indicating a joiner for a concatenate operation:


```python
from frictionless import Table

with Table('data/capital-3.csv', headers=[[1,2,3], '/']) as table:
    pprint(table.header)
    pprint(table.read_rows())
```

    ['id/1/2', 'name/London/Berlin']
    [Row([('id/1/2', 3), ('name/London/Berlin', 'Paris')]),
     Row([('id/1/2', 4), ('name/London/Berlin', 'Madrid')]),
     Row([('id/1/2', 5), ('name/London/Berlin', 'Rome')])]


## Integrity Options

Extraction function and classes accepts a few options that are needed to manage integrity behaviour:

### On Error

This option accept one of the three possible values configuring an `extract`, `Table`, `Resource` or `Package` behaviour if there is an error during the row reading process:
- ignore (default)
- warn
- raise

Let's investigate how we can add warnings on all header/row errors:


```python
from frictionless import Table

data = [["name"], [1], [2], [3]]
schema = {"fields": [{"name": "name", "type": "string"}]}
with  Table(data, schema=schema, onerror="warn") as table:
  table.read_rows()
```

    /home/roll/projects/frictionless-py/frictionless/table.py:771: UserWarning: The cell "1" in row at position "2" and field "name" at position "1" has incompatible type: type is "string/default"
      warnings.warn(error.message, UserWarning)
    /home/roll/projects/frictionless-py/frictionless/table.py:771: UserWarning: The cell "2" in row at position "3" and field "name" at position "1" has incompatible type: type is "string/default"
      warnings.warn(error.message, UserWarning)
    /home/roll/projects/frictionless-py/frictionless/table.py:771: UserWarning: The cell "3" in row at position "4" and field "name" at position "1" has incompatible type: type is "string/default"
      warnings.warn(error.message, UserWarning)


In some cases, we need to fail on the first error. We will use `raise` for it:


```python
from frictionless import Table

data = [["name"], [1], [2], [3]]
schema = {"fields": [{"name": "name", "type": "string"}]}
resource = Resource(data=data, schema=schema)
resource.onerror = 'raise' # for Resource/Package it's possible to set this property after initialization
try:
  resource.read_rows()
except Exception as exception:
  print(exception)
```

    [type-error] The cell "1" in row at position "2" and field "name" at position "1" has incompatible type: type is "string/default"


### Lookup

The lookup is a special object providing relational information in cases when it's not possible to extract. For example, the Package is capable of getting a lookup object from its resource while a table object needs it to be provided. Let's see an example:


```python
from frictionless import Table

source = [["name"], [1], [2], [4]]
lookup = {"other": {("name",): {(1,), (2,), (3,)}}}
fk = {"fields": ["name"], "reference": {"fields": ["name"], "resource": "other"}}
with Table(source, lookup=lookup, patch_schema={"foreignKeys": [fk]}) as table:
    for row in table:
        if row.row_number == 3:
            assert row.valid is False
            assert row.errors[0].code == "foreign-key-error"
            continue
        assert row.valid

```
