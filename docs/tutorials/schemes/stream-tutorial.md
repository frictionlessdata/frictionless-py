---
title: Stream Tutorial
sidebar_label: Stream
---

Frictionless supports loading Stream data.

## Reading Stream Data

> It's recommended to open files in byte-mode. If the file is opened in text-mode, Frictionless will try to re-open it in byte-mode.

You can read Stream using `Package/Resource` or `Table` [API](/docs/references/api-reference), for example:

```python title="Python"
from frictionless import Resource

with open('data/table.csv', 'rb') as file:
  resource = Resource(file, format='csv')
  print(resource.read_rows())
```
```
[Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]
```

## Writing Stream Data

The same can be done for writing CSV:

```python title="Python"
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='stream', format='csv')
```
```
<_io.BufferedReader name='/tmp/tmplh6mlh54'>
```

## Configuring Stream Data

There are no options available in `StreamControl`.

References:
- [Stream Control](../../references/schemes-reference.md#stream)
