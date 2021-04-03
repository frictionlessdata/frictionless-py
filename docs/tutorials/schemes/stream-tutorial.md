---
title: Stream Tutorial
sidebar_label: Stream
---

Frictionless supports using data stored as File-Like objects in Python.

## Reading Data

> It's recommended to open files in byte-mode. If the file is opened in text-mode, Frictionless will try to re-open it in byte-mode.

You can read Stream using `Package/Resource`, for example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

with open('data/table.csv', 'rb') as file:
  resource = Resource(file, format='csv')
  pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

A similiar approach can be used for writing:

```python goodread title="Python"
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(scheme='stream', format='csv')
pprint(target)
pprint(target.read_rows())
```
```
{'data': <_io.BufferedReader name='/tmp/tmpaxbiv_8_'>,
 'format': 'csv',
 'scheme': 'stream'}
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}]
```

## Configuring Data

There are no options available for `StreamControl`.

References:
- [Stream Control](../../references/schemes-reference.md#stream)
