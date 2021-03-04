---
title: Stream Tutorial
sidebar_label: Stream
---

Frictionless supports loading Stream data.

## Reading Stream Data

You can read Stream using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

with open('data/table.csv', 'rb') as file:
  resource = Resource(file, format='csv')
  print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Stream Data

The same is actual for writing CSV:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='stream', format='csv')
```




    <_io.BufferedReader name='/tmp/tmplh6mlh54'>



## Configuring Stream Data

There are no options available in `StreamControl`.

References:
- [Stream Control](../../references/schemes-reference.md#stream)
