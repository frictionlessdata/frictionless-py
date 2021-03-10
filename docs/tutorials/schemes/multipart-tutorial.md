---
title: Multipart Tutorial
sidebar_label: Multipart
---

> This functionality requires an experimental `multipart` plugin. [Read More](../../references/plugins-reference.md)

You can read and write files split into chunks with Frictionless.

## Reading Multipart Data

You can read using `Package/Resource` or `Table` API, for example:

```python title="Python"
from frictionless import Resource

resource = Resource(path=['data/chunk1.csv', 'data/chunk2.csv'])
print(resource.read_rows())
```
```
[Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]
```

## Writing Multipart Data

The actual for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.json')
resource.write('tmp/table{number}.json', scheme="multipart", control={"chunkSize": 1000000})
```

## Configuring Local Data

There is a control to configure how Frictionless read files using this scheme. For example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.multipart import MultipartControl

control = MultipartControl(chunk_size=1000000)
resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table{number}.json', scheme="multipart", control=control)
```

References:
- [Multipart Control](../../references/schemes-reference.md#multipart)
