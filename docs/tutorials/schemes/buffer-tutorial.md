---
title: Buffer Tutorial
sidebar_label: Buffer
---

Frictionless supports reading bytes loaded into from memory.

## Reading Buffer Data

You can read Buffer Data using `Package/Resource` or `Table` API, for example:

```python title="Python"
from frictionless import Resource

resource = Resource(b'id,name\n1,english\n2,german', format='csv')
print(resource.read_rows())
```
```
[Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', 'german')])]
```

## Writing Buffer Data

The same is actual for writing Buffer Data:

```python title="Python"
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='buffer', format='csv')
```
```
b'id,name\r\n1,english\r\n2,german\r\n'
```

## Configuring Buffer Data

There are no options available in `BufferControl`.

References:
- [Buffer Control](../../references/schemes-reference.md#buffer)
