---
title: Layout Guide
---

The Layout concept give us an ability to manage table header and pick/skip arbitrary fields and rows from the raw data stream.

```bash script title="CLI"
cat data/matrix.csv
```
```csv
f1,f2,f3,f4
11,12,13,14
21,22,23,24
31,32,33,34
41,42,43,44
```

## Layout Usage

The Layout class instance are accepted by many classes and functions:

- Resource
- describe
- extract
- validate
- and more

You just need to create a Layout instance using desired options and pass to the classed and function from above.

## Layout Options

Let's list all the available Layout options with simple usage examples:

### Header

It's a boolean flag which defaults to `True` indicating whether the data has a header row or not. In the following example the header row will be treated as a data row:

```python script title="Python"
from pprint import pprint
from frictionless import Resource, Layout

layout = Layout(header=False)
with Resource('data/capital-3.csv', layout=layout) as resource:
  pprint(resource.header.labels)
  pprint(resource.read_rows())
```
```
[]
[{'field1': 'id', 'field2': 'name'},
 {'field1': '1', 'field2': 'London'},
 {'field1': '2', 'field2': 'Berlin'},
 {'field1': '3', 'field2': 'Paris'},
 {'field1': '4', 'field2': 'Madrid'},
 {'field1': '5', 'field2': 'Rome'}]
```

### Header Rows

If header is `True` which is default, this parameters indicates where to find the header row or header rows for a multiline header. Let's see on example how the first two data rows can be treated as a part of a header:

```python script title="Python"
from pprint import pprint
from frictionless import Resource, Layout

layout = Layout(header_rows=[1, 2, 3])
with Resource('data/capital-3.csv', layout=layout) as resource:
  pprint(resource.header)
  pprint(resource.read_rows())
```
```
['id 1 2', 'name London Berlin']
[{'id 1 2': 3, 'name London Berlin': 'Paris'},
 {'id 1 2': 4, 'name London Berlin': 'Madrid'},
 {'id 1 2': 5, 'name London Berlin': 'Rome'}]
```

### Header Join

If there are multiple header rows which is managed by `header_rows` parameter, we can set a string to be a separator for a header's cell join operation. Usually it's very handy for some "fancy" Excel files. For the sake of simplicity, we will show on a CSV file:

```python script title="Python"
from pprint import pprint
from frictionless import Resource, Layout

layout = Layout(header_rows=[1, 2, 3], header_join='/')
with Resource('data/capital-3.csv', layout=layout) as resource:
  pprint(resource.header)
  pprint(resource.read_rows())
```
```
['id/1/2', 'name/London/Berlin']
[{'id/1/2': 3, 'name/London/Berlin': 'Paris'},
 {'id/1/2': 4, 'name/London/Berlin': 'Madrid'},
 {'id/1/2': 5, 'name/London/Berlin': 'Rome'}]
```

### Header Case

By default a header is validated in a case sensitive mode. To disable this behaviour we can set the `header_case` parameter to `False`. This option is accepted by any Layout and a dialect can be passed to `extract`, `validate` and other functions. Please note that it doesn't affect a resulting header it only affects how it's validated:

```python script title="Python"
from pprint import pprint
from frictionless import Resource, Schema, Field, Layout

layout = Layout(header_case=False)
schema = Schema(fields=[Field(name="ID"), Field(name="NAME")])
with Resource('data/capital-3.csv', layout=layout, schema=schema) as resource:
  print(f'Header: {resource.header}')
  print(f'Valid: {resource.header.valid}')  # without "header_case" it will have 2 errors
```
```
Header: ['ID', 'NAME']
Valid: True
```

### Pick/Skip Fields

We can pick and skip arbitrary fields based on a header row. These options accept a list of field numbers, a list of strings or a regex to match. All the queries below do the same thing for this file:

```python script title="Python"
from frictionless import extract, Layout

print(extract('data/matrix.csv', layout=Layout(pick_fields=[2, 3])))
print(extract('data/matrix.csv', layout=Layout(skip_fields=[1, 4])))
print(extract('data/matrix.csv', layout=Layout(pick_fields=['f2', 'f3'])))
print(extract('data/matrix.csv', layout=Layout(skip_fields=['f1', 'f4'])))
print(extract('data/matrix.csv', layout=Layout(pick_fields=['<regex>f[23]'])))
print(extract('data/matrix.csv', layout=Layout(skip_fields=['<regex>f[14]'])))
```
```
[{'f2': 12, 'f3': 13}, {'f2': 22, 'f3': 23}, {'f2': 32, 'f3': 33}, {'f2': 42, 'f3': 43}]
[{'f2': 12, 'f3': 13}, {'f2': 22, 'f3': 23}, {'f2': 32, 'f3': 33}, {'f2': 42, 'f3': 43}]
[{'f2': 12, 'f3': 13}, {'f2': 22, 'f3': 23}, {'f2': 32, 'f3': 33}, {'f2': 42, 'f3': 43}]
[{'f2': 12, 'f3': 13}, {'f2': 22, 'f3': 23}, {'f2': 32, 'f3': 33}, {'f2': 42, 'f3': 43}]
[{'f2': 12, 'f3': 13}, {'f2': 22, 'f3': 23}, {'f2': 32, 'f3': 33}, {'f2': 42, 'f3': 43}]
[{'f2': 12, 'f3': 13}, {'f2': 22, 'f3': 23}, {'f2': 32, 'f3': 33}, {'f2': 42, 'f3': 43}]
```

### Limit/Offset Fields

There are two options that provide an ability to limit amount of fields similar to SQL's directives:

```python script title="Python"
from frictionless import extract, Layout

print(extract('data/matrix.csv', layout=Layout(limit_fields=2)))
print(extract('data/matrix.csv', layout=Layout(offset_fields=2)))
```
```
[{'f1': 11, 'f2': 12}, {'f1': 21, 'f2': 22}, {'f1': 31, 'f2': 32}, {'f1': 41, 'f2': 42}]
[{'f3': 13, 'f4': 14}, {'f3': 23, 'f4': 24}, {'f3': 33, 'f4': 34}, {'f3': 43, 'f4': 44}]
```

### Pick/Skip Rows

It's alike the field counterparts but it will be compared to the first cell of a row. All the queries below do the same thing for this file but take into account that when picking we need to also pick a header row. In addition, there is special value `<blank>` that matches a row if it's completely blank:

```python script title="Python"
from frictionless import extract, Layout

print(extract('data/matrix.csv', layout=Layout(pick_rows=[1, 3, 4])))
print(extract('data/matrix.csv', layout=Layout(skip_rows=[2, 5])))
print(extract('data/matrix.csv', layout=Layout(pick_rows=['f1', '21', '31'])))
print(extract('data/matrix.csv', layout=Layout(skip_rows=['11', '41'])))
print(extract('data/matrix.csv', layout=Layout(pick_rows=['<regex>(f1|[23]1)'])))
print(extract('data/matrix.csv', layout=Layout(skip_rows=['<regex>[14]1'])))
print(extract('data/matrix.csv', layout=Layout(pick_rows=['<blank>'])))
```
```
[{'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}, {'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}]
[{'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}, {'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}]
[{'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}, {'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}]
[{'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}, {'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}]
[{'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}, {'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}]
[{'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}, {'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}]
[]
```

### Limit/Offset Rows

This is a quite popular option used to limit amount of rows to read:

```python script title="Python"
from frictionless import extract, Layout

print(extract('data/matrix.csv', layout=Layout(limit_rows=2)))
print(extract('data/matrix.csv', layout=Layout(offset_rows=2)))
```
```
[{'f1': 11, 'f2': 12, 'f3': 13, 'f4': 14}, {'f1': 21, 'f2': 22, 'f3': 23, 'f4': 24}]
[{'f1': 31, 'f2': 32, 'f3': 33, 'f4': 34}, {'f1': 41, 'f2': 42, 'f3': 43, 'f4': 44}]
```
