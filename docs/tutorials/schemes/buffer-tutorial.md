---
title: Buffer Tutorial
sidebar_label: Buffer
---

Frictionless supports working with bytes loaded into memory.

## Reading Data

You can read Buffer Data using `Package/Resource` API, for example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(b'id,name\n1,english\n2,german', format='csv')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}]
```

## Writing Data

A similiar approach can be used for writing:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(scheme='buffer', format='csv')
pprint(target)
pprint(target.read_rows())
```
```
{'data': b'id,name\r\n1,english\r\n2,german\r\n',
 'format': 'csv',
 'scheme': 'buffer'}
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}]
```

## Configuring Data

There are no options available for `BufferControl`.

References:
- [Buffer Control](../../references/schemes-reference.md#buffer)
