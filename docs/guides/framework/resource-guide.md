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

## Resource Lifecycle

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

## Resource Options

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
