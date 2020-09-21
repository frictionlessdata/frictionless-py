# Extracting Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1is_PcpzFl42aWI2B2tHaBGj3jxsKZ_eZ)



Extracting data means reading tabular data from some source. We can use various customizations for this process such as providing a file format, table schema, limiting fields or rows amount, and much more. Let's see this with real files:


```bash
! pip install frictionless
```


```bash
! wget -q -O country-3.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-3.csv
! cat country-3.csv
```

    id,capital_id,name,population
    1,1,Britain,67
    2,3,France,67
    3,2,Germany,83
    4,5,Italy,60
    5,4,Spain,47



```bash
! wget -q -O capital-3.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv
! cat capital-3.csv
```

    id,name
    1,London
    2,Berlin
    3,Paris
    4,Madrid
    5,Rome


For a starter, we will use the command-line interface:


```bash
! frictionless extract country-3.csv
```

    [data] country-3.csv

      id    capital_id  name       population
    ----  ------------  -------  ------------
       1             1  Britain            67
       2             3  France             67
       3             2  Germany            83
       4             5  Italy              60
       5             4  Spain              47


The same can be done in Python:


```python
from pprint import pprint
from frictionless import extract

rows = extract('country-3.csv')
pprint(rows)
```

    [Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
     Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
     Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
     Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
     Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]


## Extract Functions

The high-level interface for extracting data provided by Frictionless is a set of `extract` functions:
- `extract`: it will detect the source type and extract data accordingly
- `extract_package`: it accepts a package descriptor and returns a map of the package's tables
- `extract_resource`: it accepts a resource descriptor and returns a table data
- `extract_table`: it accepts various tabular options and returns a table data

In command-line, there is only 1 command but there is a flag to adjust the behavior:

```bash
$ frictionless extract
$ frictionless extract --source-type package
$ frictionless extract --source-type resource
$ frictionless extract --source-type table
```


The `extract` functions always read data in a form of rows (see the object description below) into memory. The lower-level interfaces will allow you to stream data and various output forms.


### Extracting a Package

Let's start by using the command line-interface. We're going to provide two files to the `extract` command which will be enough to detect that it's a dataset:


```bash
! frictionless extract *-3.csv
```

    [data] capital-3.csv

      id  name
    ----  ------
       1  London
       2  Berlin
       3  Paris
       4  Madrid
       5  Rome

    [data] country-3.csv

      id    capital_id  name       population
    ----  ------------  -------  ------------
       1             1  Britain            67
       2             3  France             67
       3             2  Germany            83
       4             5  Italy              60
       5             4  Spain              47


In Python we can do the same by providing a glob for the `extract` function, but instead we will use `extract_package` by providing a package descriptor:


```python
from frictionless import extract_package

data = extract_package({'resources':[{'path': 'country-3.csv'}, {'path': 'capital-3.csv'}]})
for path, rows in data.items():
  pprint(path)
  pprint(rows)
```

    'country-3.csv'
    [Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
     Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
     Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
     Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
     Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]
    'capital-3.csv'
    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', 3), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]


### Extracting Resource

A resource contains only one file and for extracting a resource we can use the same approach we used above but providing only one file. We will extract data using a metadata descriptor:


```python
from frictionless import extract_resource

rows = extract_resource({'path': 'capital-3.csv'})
pprint(rows)
```

    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', 3), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]


Usually, the code above doesn't really make sense as we can just provide a path to the high-level `extract` function instead of a descriptor to the `extract_resource` function but the power of the descriptor is that it can contain different metadata and be stored on the disc. Let's extend our example:


```python
from frictionless import Resource

resource = Resource(path='capital-3.csv')
resource.schema.missing_values.append('3')
resource.to_yaml('capital.resource.yaml')
```


```bash
! cat capital.resource.yaml
```

    path: capital-3.csv
    schema:
      missingValues:
        - ''
        - '3'



```bash
! frictionless extract capital.resource.yaml
```

    [data] capital.resource.yaml

      id  name
    ----  ------
       1  London
       2  Berlin
          Paris
       4  Madrid
       5  Rome


So what's happened? We set textual representation of the number "3" to be a missing value. It was done only for the presentational purpose because it's definitely not a missing value. On the other hand, it demonstrated how metadata can be used.

### Extracting a Table

While the package and resource concepts contain both data and metadata, a table is solely data. Because of this fact we can provide many more options to the `extract_table` function. Most of these options are encapsulated into the resource descriptor as we saw with the `missingValues` example above. We will reproduce it:


```python
from frictionless import extract_table

rows = extract_table('capital-3.csv', patch_schema={'missingValues': ['', '3']})
pprint(rows)
```

    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', None), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]


We got an identical result but it's important to understand that on the table level we need to provide all the metadata options separately while a resource encapsulate all these metadata. Please check the `extract_table` API Reference as it has a lot of options. We're going to discuss some of them below.

## Extraction Options

All the `extract` fuctions accept only one common argument:
- `process`: it's a function getting a row object and returning whatever is needed as an ouput of the data extraction e.g. `lambda row: row.to_dict()`


**Package/Resource**

These `extract` functions doesn't accept any additional arguments.

**Table**

We will take a look at all the `extract_table` options in the sections below. As an overview, it accepts:
- File Details
- File Control
- Table Dialect
- Table Query
- Header Options
- Schema Options
- Integrity Options
- Infer Options (see "Describing Data")

## Using Package

The Package class is a metadata class which provides an ability to read its contents. First of all, let's create a package descriptor:


```bash
! frictionless describe *-3.csv --json > country.package.json
```

Now, we can open the created descriptor and read the package's resources:


```python
from frictionless import Package

package = Package('country.package.json')
pprint(package.get_resource('country-3').read_rows())
pprint(package.get_resource('capital-3').read_rows())
```

    [Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
     Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
     Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
     Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
     Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]
    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', 3), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]


The package by itself doesn't provide any read functions directly as it's a role of its resources. So everything written below for the Resource class can be used within a package.


## Using Resource

The Resource class is also a metadata class which provides various read and stream functions. Let's create a resource descriptor:


```bash
! frictionless describe country-3.csv --json > country.resource.json
```

**Exploring Data**

There are various functions to help explore your resource, such as checking a header or other attributes like stats:


```python
from frictionless import Resource

resource = Resource('country.resource.json')
pprint(resource.read_header())
pprint(resource.read_sample())
pprint(resource.read_stats())
```

    ['id', 'capital_id', 'name', 'population']
    [['1', '1', 'Britain', '67'],
     ['2', '3', 'France', '67'],
     ['3', '2', 'Germany', '83'],
     ['4', '5', 'Italy', '60'],
     ['5', '4', 'Spain', '47']]
    {'bytes': 100, 'hash': 'c0558b91523683483f86f63346d06d81', 'rows': 5}


**Reading Data**

The `extract` functions always read rows into memory; Resource can do the same but it also gives a choice regarding ouput data. It can be `rows`, `data`, `text`, or `bytes`. Let's try reading all of them:


```python
from frictionless import Resource

resource = Resource('country.resource.json')
pprint(resource.read_bytes())
pprint(resource.read_text())
pprint(resource.read_data())
pprint(resource.read_rows())
```

    (b'id,capital_id,name,population\n1,1,Britain,67\n2,3,France,67\n3,2,Germany,8'
     b'3\n4,5,Italy,60\n5,4,Spain,47\n')
    ('id,capital_id,name,population\n'
     '1,1,Britain,67\n'
     '2,3,France,67\n'
     '3,2,Germany,83\n'
     '4,5,Italy,60\n'
     '5,4,Spain,47\n')
    [['1', '1', 'Britain', '67'],
     ['2', '3', 'France', '67'],
     ['3', '2', 'Germany', '83'],
     ['4', '5', 'Italy', '60'],
     ['5', '4', 'Spain', '47']]
    [Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
     Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
     Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
     Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
     Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]


**Streaming Data**

It's really handy to read all your data into memory but it's not always possible as a file can be really big. For such cases, Frictionless provides streaming functions:


```python
from frictionless import Resource

resource = Resource('country.resource.json')
pprint(resource.read_byte_stream())
pprint(resource.read_text_stream())
pprint(resource.read_data_stream())
pprint(resource.read_row_stream())
for row in resource.read_row_stream():
  print(row)
```

    <frictionless.loader.ByteStreamWithStatsHandling object at 0x7f14758c8c88>
    <_io.TextIOWrapper name='country-3.csv' encoding='utf-8'>
    <generator object Resource.read_data_stream at 0x7f147591aa98>
    <generator object Resource.read_row_stream at 0x7f147591aa98>
    Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)])
    Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)])
    Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)])
    Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)])
    Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])


## Using Table

The Table class is at the heart of all the tabular capabilities of Frictionless. It's used by all the higher-level classes and provides a comprehensive user interface by itself. The main difference with, for example, Resource class is that Table has a state of a lower-level file descriptor and needs to be opened and closed. Usually we use a context manager (the `with` keyword) to work with Table. In-general, Table is a streaming interface that needs to be re-opened if data is already read.


**Exploring Data**

First of all, let's take a look at the file details information:



```python
from frictionless import Table

with Table('capital-3.csv') as table:
  print(f'Source: "{table.source}"')
  print(f'Scheme: "{table.scheme}"')
  print(f'Format: "{table.format}"')
  print(f'Hashing: "{table.hashing}"')
  print(f'Encoding: "{table.encoding}"')
  print(f'Compression: "{table.compression}"')
  print(f'Compression Path: "{table.compression_path}"')
```

    Source: "capital-3.csv"
    Scheme: "file"
    Format: "csv"
    Hashing: "md5"
    Encoding: "utf-8"
    Compression: "no"
    Compression Path: ""


There is much more information available; we will explain some of it later in the sections below:


```python
from frictionless import Table

with Table('capital-3.csv') as table:
  print(f'Control: "{table.control}"')
  print(f'Dialect: "{table.dialect}"')
  print(f'Query: "{table.query}"')
  print(f'Header: "{table.header}"')
  print(f'Schema: "{table.schema}"')
  print(f'Sample: "{table.sample}"')
  print(f'Stats: "{table.stats}"')
```

    Control: "{}"
    Dialect: "{}"
    Query: "{}"
    Header: "['id', 'name']"
    Schema: "{'fields': [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]}"
    Sample: "[['1', 'London'], ['2', 'Berlin'], ['3', 'Paris'], ['4', 'Madrid'], ['5', 'Rome']]"
    Stats: "{'hash': 'e7b6592a0a4356ba834e4bf1c8e8c7f8', 'bytes': 50, 'rows': 0}"


Many of the properties above not only can be read from the existent Table but also can be provided as an option to alter the Table behaviour, for example:


```python
from frictionless import Table

with Table('capital-3.csv', scheme='file', format='csv') as table:
  print(table.source)
  print(table.scheme)
  print(table.format)
```

    capital-3.csv
    file
    csv


**Reading Data**

There are 2 different types of ouput that Table can produce:


```python
from frictionless import Table

with Table('capital-3.csv') as table:
  pprint(table.read_data())
with Table('capital-3.csv') as table:
  pprint(table.read_rows())
```

    [['1', 'London'],
     ['2', 'Berlin'],
     ['3', 'Paris'],
     ['4', 'Madrid'],
     ['5', 'Rome']]
    [Row([('id', 1), ('name', 'London')]),
     Row([('id', 2), ('name', 'Berlin')]),
     Row([('id', 3), ('name', 'Paris')]),
     Row([('id', 4), ('name', 'Madrid')]),
     Row([('id', 5), ('name', 'Rome')])]


The `data` format is just a raw array of arrays similiar to JSON while the `row` format is a rich object with all the cells normalized and converted to proper types. We will explore the Row class later.

**Streaming Data**

It was mentioned for Resource and it's the same for Table, we can stream our tabular data. The core difference is that Table is stateful so we use properties instead of the read functions:


```python
from frictionless import Table

with Table('capital-3.csv') as table:
  pprint(table.data_stream)
  for cells in table.data_stream:
    print(cells)
with Table('capital-3.csv') as table:
  pprint(table.row_stream)
  for row in table.row_stream:
    print(row)
```

    <generator object Table.__read_data_stream_create at 0x7f14758c6ba0>
    ['1', 'London']
    ['2', 'Berlin']
    ['3', 'Paris']
    ['4', 'Madrid']
    ['5', 'Rome']
    <generator object Table.__read_row_stream_create at 0x7f147591ae60>
    Row([('id', 1), ('name', 'London')])
    Row([('id', 2), ('name', 'Berlin')])
    Row([('id', 3), ('name', 'Paris')])
    Row([('id', 4), ('name', 'Madrid')])
    Row([('id', 5), ('name', 'Rome')])


**Table's Lifecycle**

You might have noticed that we had to duplicate the `with Table(...)` statement in some examples. The reason is that Table is a streaming interface. Once it's read you need to open it again. Let's show it in an example:


```python
from frictionless import Table

table = Table('capital-3.csv')
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

**Scheme**

The scheme also know as protocol indicates which loader Frictionless should use to read or write data. It can be `file` (default), `text`, `http`, `https`, `s3`, and others.


```python
from frictionless import Table

with Table('header1,header2\nvalue1,value2.csv', scheme='text') as table:
  print(table.scheme)
  print(table.read_rows())
```

    text
    [Row([('header1', 'value1'), ('header2', 'value2.csv')])]


**Format**

The format or as it's also called extension helps Frictionless to choose a proper parser to handle the file. Popular formats are `csv`, `xlsx`, `json` and others


```python
from frictionless import Table

with Table('text://header1,header2\nvalue1,value2.csv', format='csv') as table:
  print(table.format)
  print(table.read_rows())
```

    csv
    [Row([('header1', 'value1'), ('header2', 'value2.csv')])]


**Hashing**

The hashing option controls which hashing algorithm should be used for generating the `hash` property. It doesn't affect the `extract` function but can be used with the `Table` class:


```python
from frictionless import Table

with Table('country-3.csv', hashing='sha256') as table:
  table.read_rows()
  print(table.hashing)
  print(table.stats['hash'])
```

    sha256
    408b5058f961915c1e1f3bc318ab01d7d094a4daccdf03ad6022cfc7b8ea4e3e


**Encoding**

Frictionless automatically detects encoding of files but sometimes it can be innacurate. It's possible to provide an encoding manually:


```python
from frictionless import Table

with Table('country-3.csv', encoding='utf-8') as table:
  print(table.encoding)
  print(table.source)
```

    utf-8
    country-3.csv


**Compression**

It's possible to adjust compression detection by providing the algorithm explicetely. For the example below it's not required as it would be detected anyway:


```bash
! wget -q -O table.csv.zip https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv.zip
```


```python
from frictionless import Table

with Table('table.csv.zip', compression='zip') as table:
  print(table.compression)
  print(table.read_rows())
```

    zip
    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


**Compression Path**

By default, Frictionless uses the first file found in a zip archive. It's possible to adjust this behaviour:


```bash
! wget -q -O table-multiple-files.zip https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table-multiple-files.zip
```


```python
from frictionless import Table

with Table('table-multiple-files.zip', compression_path='table-reverse.csv') as table:
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
from frictionless import Table, controls

source = 'https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv'
control = controls.RemoteControl(http_timeout=1)
with Table(source, control=control) as table:
  print(table.control)
  print(table.read_rows())
```

    {'httpTimeout': 1}
    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


Exact parameters depend on schemes and can be found in the "Schemes Reference". For example, the Remote Control provides `http_timeout`, `http_session`, and others but there is only one option available for all controls:

**Detect Encoding**

It's a function that can be provided to adjust the encoding detection. This function accept a data sample and return a detected encoding:


```python
from frictionless import Table, controls

control = controls.Control(detect_encoding=lambda sample: "utf-8")
with Table("capital-3.csv", control=control) as table:
  print(table.source)
  print(table.encoding)
```

    capital-3.csv
    utf-8


Further reading:
- Schemes Reference

## Table Dialect

The Dialect adjust the way tabular parsers work. The concept is similiar to the Control above. Let's use the CSV Dialect to adjust the delimiter configuration:


```python
from frictionless import Table, dialects

source = 'header1;header2\nvalue1;value2'
dialect = dialects.CsvDialect(delimiter=';')
with Table(source, scheme='text', format='csv', dialect=dialect) as table:
  print(table.dialect)
  print(table.read_rows())
```

    {'delimiter': ';'}
    [Row([('header1', 'value1'), ('header2', 'value2')])]


There is a great deal of options available for different dialect that can be found in "Formats Reference". We will list the properties that can be used with every dialect:

**Header**

It's a boolean flag wich deaults to `True` indicating whether the data has a header row or not. In the following example the header row will be treated as a data row:


```python
from frictionless import Table, dialects

dialect = dialects.Dialect(header=False)
with Table('capital-3.csv', dialect=dialect) as table:
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


**Header Rows**

If header is `True` which is default, this parameters indicates where to find the header row or header rows for a multiline header. Let's see on example how the first two data rows can be treated as a part of a header:


```python
from frictionless import Table, dialects

dialect = dialects.Dialect(header_rows=[1, 2, 3])
with Table('capital-3.csv', dialect=dialect) as table:
  pprint(table.header)
  pprint(table.read_rows())
```

    ['id 1 2', 'name London Berlin']
    [Row([('id 1 2', 3), ('name London Berlin', 'Paris')]),
     Row([('id 1 2', 4), ('name London Berlin', 'Madrid')]),
     Row([('id 1 2', 5), ('name London Berlin', 'Rome')])]


**Header Join**

If there are multiple header rows which is managed by `header_rows` parameter, we can set a string to be a separator for a header's cell join operation. Usually it's very handy for some "fancy" Excel files. For the sake of simplicity, we will show on a CSV file:


```python
from frictionless import Table, dialects

dialect = dialects.Dialect(header_rows=[1, 2, 3], header_join='/')
with Table('capital-3.csv', dialect=dialect) as table:
  pprint(table.header)
  pprint(table.read_rows())
```

    ['id/1/2', 'name/London/Berlin']
    [Row([('id/1/2', 3), ('name/London/Berlin', 'Paris')]),
     Row([('id/1/2', 4), ('name/London/Berlin', 'Madrid')]),
     Row([('id/1/2', 5), ('name/London/Berlin', 'Rome')])]


Further reading:
- Formats Reference

## Table Query

Using header management described in the "Table Dialect" section we can have a basic skipping rows ability e.g. if we set `dialect.header_rows=[2]` we will skip the first row but it's very limited. There is a much more powerful interface called Table Queries to indicate where exactly to get tabular data from a file. We will use a simple file looking like a matrix:


```bash
! wget -q -O matrix.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/matrix.csv
! cat matrix.csv
```

    f1,f2,f3,f4
    11,12,13,14
    21,22,23,24
    31,32,33,34
    41,42,43,44


**Pick/Skip Fields**

We can pick and skip arbitrary fields based on a header row. These options accept a list of field numbers, a list of strings or a regex to match. All the queries below do the same thing for this file:


```python
from frictionless import extract, Query

print(extract('matrix.csv', query=Query(pick_fields=[2, 3])))
print(extract('matrix.csv', query=Query(skip_fields=[1, 4])))
print(extract('matrix.csv', query=Query(pick_fields=['f2', 'f3'])))
print(extract('matrix.csv', query=Query(skip_fields=['f1', 'f4'])))
print(extract('matrix.csv', query=Query(pick_fields=['<regex>f[23]'])))
print(extract('matrix.csv', query=Query(skip_fields=['<regex>f[14]'])))
```

    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]
    [Row([('f2', 12), ('f3', 13)]), Row([('f2', 22), ('f3', 23)]), Row([('f2', 32), ('f3', 33)]), Row([('f2', 42), ('f3', 43)])]


**Limit/Offset Fields**

There are two options that provide an ability to limit amount of fields similiar to SQL's directives:


```python
from frictionless import extract, Query

print(extract('matrix.csv', query=Query(limit_fields=2)))
print(extract('matrix.csv', query=Query(offset_fields=2)))
```

    [Row([('f1', 11), ('f2', 12)]), Row([('f1', 21), ('f2', 22)]), Row([('f1', 31), ('f2', 32)]), Row([('f1', 41), ('f2', 42)])]
    [Row([('f3', 13), ('f4', 14)]), Row([('f3', 23), ('f4', 24)]), Row([('f3', 33), ('f4', 34)]), Row([('f3', 43), ('f4', 44)])]


**Pick/Skip Rows**

It's alike the field counterparts but it will be compared to the first cell of a row. All the queries below do the same thing for this file but take into account that when picking we need to also pick a header row. In addition, there is special value `<blank>` that matches a row if it's competely blank:


```python
from frictionless import extract, Query

print(extract('matrix.csv', query=Query(pick_rows=[1, 3, 4])))
print(extract('matrix.csv', query=Query(skip_rows=[2, 5])))
print(extract('matrix.csv', query=Query(pick_rows=['f1', '21', '31'])))
print(extract('matrix.csv', query=Query(skip_rows=['11', '41'])))
print(extract('matrix.csv', query=Query(pick_rows=['<regex>(f1|[23]1)'])))
print(extract('matrix.csv', query=Query(skip_rows=['<regex>[14]1'])))
print(extract('matrix.csv', query=Query(pick_rows=['<blank>'])))
```

    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    [Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)]), Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)])]
    []


**Limit/Offset Rows**

It's a quite popular option used to limit amount of rows to read:


```python
from frictionless import extract, Query

print(extract('matrix.csv', query=Query(limit_rows=2)))
print(extract('matrix.csv', query=Query(offset_rows=2)))
```

    [Row([('f1', 11), ('f2', 12), ('f3', 13), ('f4', 14)]), Row([('f1', 21), ('f2', 22), ('f3', 23), ('f4', 24)])]
    [Row([('f1', 31), ('f2', 32), ('f3', 33), ('f4', 34)]), Row([('f1', 41), ('f2', 42), ('f3', 43), ('f4', 44)])]


## Header Options

Header management is a responsibility of "Table Dialect" which will be described below but Table accept a special `headers` argument that plays a role of a high-level helper in setting different header options.


It accepts a `False` values indicating that there is no header row:


```python
from frictionless import Table

with Table('capital-3.csv', headers=False) as table:
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

with Table('capital-3.csv', headers=2) as table:
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

with Table('capital-3.csv', headers=[1,2,3]) as table:
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

with Table('capital-3.csv', headers=[[1,2,3], '/']) as table:
    pprint(table.header)
    pprint(table.read_rows())
```

    ['id/1/2', 'name/London/Berlin']
    [Row([('id/1/2', 3), ('name/London/Berlin', 'Paris')]),
     Row([('id/1/2', 4), ('name/London/Berlin', 'Madrid')]),
     Row([('id/1/2', 5), ('name/London/Berlin', 'Rome')])]


## Schema Options

By default, a schema for a table is inferred under the hood but we can also pass it explicetely.

**Schema**

The most common way is providing a schema argument to the Table constructor. For example, let's make the `id` field be a string instead of an integer:


```python
from frictionless import Table, Schema, Field

schema = Schema(fields=[Field(name='id', type='string'), Field(name='name', type='string')])
with Table('capital-3.csv', schema=schema) as table:
  pprint(table.schema)
  pprint(table.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'string'},
                {'name': 'name', 'type': 'string'}]}
    [Row([('id', '1'), ('name', 'London')]),
     Row([('id', '2'), ('name', 'Berlin')]),
     Row([('id', '3'), ('name', 'Paris')]),
     Row([('id', '4'), ('name', 'Madrid')]),
     Row([('id', '5'), ('name', 'Rome')])]


**Sync Schema**

There is a way to sync provided schema based on a header row's field order. It's very useful when you have a schema that represents only a subset of the table's fields:


```python
from frictionless import Table, Schema, Field

# Note the order of the fields
schema = Schema(fields=[Field(name='name', type='string'), Field(name='id', type='string')])
with Table('capital-3.csv', schema=schema, sync_schema=True) as table:
  pprint(table.schema)
  pprint(table.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'string'},
                {'name': 'name', 'type': 'string'}]}
    [Row([('id', '1'), ('name', 'London')]),
     Row([('id', '2'), ('name', 'Berlin')]),
     Row([('id', '3'), ('name', 'Paris')]),
     Row([('id', '4'), ('name', 'Madrid')]),
     Row([('id', '5'), ('name', 'Rome')])]


**Patch Schema**

Sometimes we just want to update only a few fields or some schema's properties without providing a brand new schema. For example, the two examples above can be simplified as:


```python
from frictionless import Table

with Table('capital-3.csv', patch_schema={'fields': {'id': {'type': 'string'}}}) as table:
  pprint(table.schema)
  pprint(table.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'string'},
                {'name': 'name', 'type': 'string'}]}
    [Row([('id', '1'), ('name', 'London')]),
     Row([('id', '2'), ('name', 'Berlin')]),
     Row([('id', '3'), ('name', 'Paris')]),
     Row([('id', '4'), ('name', 'Madrid')]),
     Row([('id', '5'), ('name', 'Rome')])]


## Integrity Options

Exctraction function and classes accepts only one integrity option:


**Lookup**

The lookup is a special object providing relational information in cases when it's not impossible to extract. For example, the Package is capable to get a lookup object from its resource while a table object needs it to be provided. Let's see on an example:


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

## Header Object

After opening a table or calling `resource.read_header` you get an access to a `header` object. It's a list but providing some additional functionality. Let's take a look:




```python
from frictionless import Table

with Table('capital-3.csv') as table:
  print(f'Header: {table.header}')
  print(f'Schema: {table.header.schema}')
  print(f'Field Positions: {table.header.field_positions}')
  print(f'Errors: {table.header.errors}')
  print(f'Valid: {table.header.valid}')
  print(f'As Dict: {table.header.to_dict()}') # field name: header cell
  print(f'As List: {table.header.to_list()}')
```

    Header: ['id', 'name']
    Schema: {'fields': [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]}
    Field Positions: [1, 2]
    Errors: []
    Valid: True
    As Dict: {'id': 'id', 'name': 'name'}
    As List: ['id', 'name']


The example above covers the case when a header is valid. For a header with tabular errors this information can be much more useful revealing discrepancies, dublicates or missing cells information. Please read "API Reference" for more details.

## Row Object

The `extract`, `resource.read_rows()`, `table.read_rows()`, and many other functions retunrs or yeilds row objects. It's a `OrderedDict` providing additional API shown below:



```python
from frictionless import Table

with Table('capital-3.csv', patch_schema={'missingValues': ['1']}) as table:
  for row in table:
    print(f'Row: {row}')
    print(f'Schema: {row.schema}')
    print(f'Field Positions: {row.field_positions}')
    print(f'Row Position: {row.row_position}') # physical line number starting from 1
    print(f'Row Number: {row.row_number}') # counted row number starting from 1
    print(f'Blank Cells: {row.blank_cells}')
    print(f'Error Cells: {row.error_cells}')
    print(f'Errors: {row.errors}')
    print(f'Valid: {row.valid}')
    print(f'As Dict: {row.to_dict(json=False)}')
    print(f'As List: {row.to_list(json=True)}') # JSON compatible data types
    break
```

    Row: Row([('id', None), ('name', 'London')])
    Schema: {'fields': [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}], 'missingValues': ['1']}
    Field Positions: [1, 2]
    Row Position: 2
    Row Number: 1
    Blank Cells: {'id': '1'}
    Error Cells: {}
    Errors: []
    Valid: True
    As Dict: {'id': None, 'name': 'London'}
    As List: [None, 'London']


As we can see, it provides a lot of information which is especially useful when a row is not valid. Our row is valid but we demostrated how it can preserve data about raw missing values. It also preserves data about all errored cells. Please read "API Reference" for more details.