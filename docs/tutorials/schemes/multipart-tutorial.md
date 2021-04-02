---
title: Multipart Tutorial
sidebar_label: Multipart
---

> This functionality requires an experimental `multipart` plugin. [Read More](../../references/plugins-reference.md)

You can read and write files split into chunks with Frictionless.

## Reading Data

You can read using `Package/Resource`, for example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path=['data/chunk1.csv', 'data/chunk2.csv'])
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

The actual for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.json')
resource.write('tmp/table{number}.json', scheme="multipart", control={"chunkSize": 1000000})
```

## Using Control

There is a control to configure how Frictionless handle files using this scheme. For example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.multipart import MultipartControl

control = MultipartControl(chunk_size=1000000)
resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table{number}.json', scheme="multipart", control=control)
```

References:
- [Multipart Control](../../references/schemes-reference.md#multipart)
