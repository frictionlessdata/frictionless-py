---
title: Extracting Data
---

Extracting data means reading tabular data from some source. We can use various customizations for this process such as providing a file format, table schema, limiting fields or rows amount, and much more. Let's see this with real files:

```bash
$ cat data/country-3.csv
```

```csv
id,capital_id,name,population
1,1,Britain,67
2,3,France,67
3,2,Germany,83
4,5,Italy,60
5,4,Spain,47
```

```bash
$ cat data/capital-3.csv
```

```csv
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

For a starter, we will use the command-line interface:

```bash
$ frictionless extract data/country-3.csv
```

```
---
data: data/country-3.csv
---

==  ==========  =======  ==========
id  capital_id  name     population
==  ==========  =======  ==========
 1           1  Britain          67
 2           3  France           67
 3           2  Germany          83
 4           5  Italy            60
 5           4  Spain            47
==  ==========  =======  ==========
```

The same can be done in Python:

```python
from pprint import pprint
from frictionless import extract

rows = extract('data/country-3.csv')
pprint(rows)
```

```
[Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
 Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
 Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
 Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
 Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]
```

## Extract Functions

The high-level interface for extracting data provided by Frictionless is a set of `extract` functions:
- `extract`: it will detect the source type and extract data accordingly
- `extract_package`: it accepts a package descriptor and returns a map of the package's tables
- `extract_resource`: it accepts a resource descriptor and returns a table data

In command-line, there is only 1 command but there is a flag to adjust the behavior:

```bash
$ frictionless extract
$ frictionless extract --type package
$ frictionless extract --type resource
```

The `extract` functions always read data in a form of rows (see the object description below) into memory. The lower-level interfaces will allow you to stream data and various output forms.

## Extracting Resource

A resource contains only one file and for extracting a resource we can use the same approach we used above but providing only one file. We will extract data using a metadata descriptor:

```python
from frictionless import extract

rows = extract('data/capital-3.csv')
pprint(rows)
```

```
[Row([('id', 1), ('name', 'London')]),
 Row([('id', 2), ('name', 'Berlin')]),
 Row([('id', 3), ('name', 'Paris')]),
 Row([('id', 4), ('name', 'Madrid')]),
 Row([('id', 5), ('name', 'Rome')])]
```

Usually, the code above doesn't really make sense as we can just provide a path to the high-level `extract` function instead of a descriptor to the `extract_resource` function but the power of the descriptor is that it can contain different metadata and be stored on the disc. Let's extend our example:

```python
from frictionless import Resource

resource = Resource('data/capital-3.csv')
resource.schema.missing_values.append('3')
resource.to_yaml('tmp/capital.resource.yaml')
```

```bash
$ frictionless extract tmp/capital.resource.yaml --basepath .
```

```
---
data: tmp/capital.resource.yaml
---

====  ======
id    name
====  ======
   1  London
   2  Berlin
None  Paris
   4  Madrid
   5  Rome
====  ======
```

So what's happened? We set textual representation of the number "3" to be a missing value. It was done only for the presentational purpose because it's definitely not a missing value. On the other hand, it demonstrated how metadata can be used.

## Extracting Package

Let's start by using the command line-interface. We're going to provide two files to the `extract` command which will be enough to detect that it's a dataset:

```bash
$ frictionless extract data/*-3.csv
```

```
---
data: data/capital-3.csv
---

==  ======
id  name
==  ======
 1  London
 2  Berlin
 3  Paris
 4  Madrid
 5  Rome
==  ======

---
data: data/country-3.csv
---

==  ==========  =======  ==========
id  capital_id  name     population
==  ==========  =======  ==========
 1           1  Britain          67
 2           3  France           67
 3           2  Germany          83
 4           5  Italy            60
 5           4  Spain            47
==  ==========  =======  ==========
```

In Python we can do the same by providing a glob for the `extract` function, but instead we will use `extract_package` by providing a package descriptor:

```python
from frictionless import extract

data = extract('data/*-3.csv)
for path, rows in data.items():
  pprint(path)
  pprint(rows)
```

```
'data/country-3.csv'
[Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
 Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
 Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
 Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
 Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]
'data/capital-3.csv'
[Row([('id', 1), ('name', 'London')]),
 Row([('id', 2), ('name', 'Berlin')]),
 Row([('id', 3), ('name', 'Paris')]),
 Row([('id', 4), ('name', 'Madrid')]),
 Row([('id', 5), ('name', 'Rome')])]
```

## Resource Class

The Resource class is also a metadata class which provides various read and stream functions. The `extract` functions always read rows into memory; Resource can do the same but it also gives a choice regarding output data. It can be `rows`, `data`, `text`, or `bytes`. Let's try reading all of them:

```python
from frictionless import Resource

resource = Resource('data/country-3.csv')
pprint(resource.read_bytes())
pprint(resource.read_text())
pprint(resource.read_lists())
pprint(resource.read_rows())
```

```
(b'id,capital_id,name,population\n1,1,Britain,67\n2,3,France,67\n3,2,Germany,8'
 b'3\n4,5,Italy,60\n5,4,Spain,47\n')
('id,capital_id,name,population\n'
 '1,1,Britain,67\n'
 '2,3,France,67\n'
 '3,2,Germany,83\n'
 '4,5,Italy,60\n'
 '5,4,Spain,47\n')
[['id', 'capital_id', 'name', 'population'],
 ['1', '1', 'Britain', '67'],
 ['2', '3', 'France', '67'],
 ['3', '2', 'Germany', '83'],
 ['4', '5', 'Italy', '60'],
 ['5', '4', 'Spain', '47']]
[Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)]),
 Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)]),
 Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)]),
 Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)]),
 Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])]
```

It's really handy to read all your data into memory but it's not always possible as a file can be really big. For such cases, Frictionless provides streaming functions:

```python
from frictionless import Resource

with Resource('data/country-3.csv') as resource:
    pprint(resource.byte_stream)
    pprint(resource.text_stream)
    pprint(resource.data_stream)
    pprint(resource.row_stream)
    for row in resource.row_stream:
      print(row)
```

```
<frictionless.loader.ByteStreamWithStatsHandling object at 0x7fe7e3664910>
<_io.TextIOWrapper name='./data/country-3.csv' encoding='utf-8'>
<generator object Resource.read_data_stream at 0x7fe7e3c93a50>
<generator object Resource.read_row_stream at 0x7fe7e3c93a50>
Row([('id', 1), ('capital_id', 1), ('name', 'Britain'), ('population', 67)])
Row([('id', 2), ('capital_id', 3), ('name', 'France'), ('population', 67)])
Row([('id', 3), ('capital_id', 2), ('name', 'Germany'), ('population', 83)])
Row([('id', 4), ('capital_id', 5), ('name', 'Italy'), ('population', 60)])
Row([('id', 5), ('capital_id', 4), ('name', 'Spain'), ('population', 47)])
```

## Package Class

The Package class is a metadata class which provides an ability to read its contents. First of all, let's create a package descriptor:


```bash
$ frictionless describe data/*-3.csv --json > tmp/country.package.json
```

Now, we can open the created descriptor and read the package's resources:

```python
from frictionless import Package

package = Package('data/*-3.csv')
pprint(package.get_resource('country-3').read_rows())
pprint(package.get_resource('capital-3').read_rows())
```

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
```

The package by itself doesn't provide any read functions directly as it's a role of its resources. So everything written below for the Resource class can be used within a package.

## Header Class

After opening a resource you get access to a `resource.header` object. It's a list of normalized labels but providing some additional functionality. Let's take a look:


```python
from frictionless import Resource

with Resource('data/capital-3.csv') as resource:
  print(f'Header: {resource.header}')
  print(f'Labels: {resource.header.labels}')
  print(f'Fields: {resource.header.fields}')
  print(f'Field Names: {resource.header.field_names}')
  print(f'Field Positions: {resource.header.field_positions}')
  print(f'Errors: {resource.header.errors}')
  print(f'Valid: {resource.header.valid}')
  print(f'As List: {resource.header.to_list()}')
```

    Header: ['id', 'name']
    Labels: ['id', 'name']
    Fields: [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]
    Field Names: ['id', 'name']
    Field Positions: [1, 2]
    Errors: []
    Valid: True
    As List: ['id', 'name']


The example above covers the case when a header is valid. For a header with tabular errors this information can be much more useful revealing discrepancies, duplicates or missing cells information. Please read "API Reference" for more details.

## Row Class

The `extract`, `resource.read_rows()` and many other functions return or yield row objects. It's a `dict` providing additional API shown below:

```python
from frictionless import Resource, Detector

detector = Detector(schema_patch={'missingValues': ['1']})
with Resource('data/capital-3.csv', detector=detector) as resource:
  for row in resource:
    print(f'Row: {row}')
    print(f'Cells: {row.cells}')
    print(f'Fields: {row.fields}')
    print(f'Field Names: {row.field_names}')
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

```
Row: Row([('id', None), ('name', 'London')])
Cells: ['1', 'londong']
Fields: [{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]
Field Names: ['id', 'name']
Field Positions: [1, 2]
Row Position: 2
Row Number: 1
Blank Cells: {'id': '1'}
Error Cells: {}
Errors: []
Valid: True
As Dict: {'id': None, 'name': 'London'}
As List: [None, 'London']
```

As we can see, it provides a lot of information which is especially useful when a row is not valid. Our row is valid but we demonstrated how it can preserve data about raw missing values. It also preserves data about all errored cells. Please read "API Reference" for more details.
