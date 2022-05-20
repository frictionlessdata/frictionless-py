---
title: Buffer Tutorial
sidebar_label: Buffer
---

Frictionless supports working with bytes loaded into memory.

## Reading Data

You can read Buffer Data using `Package/Resource` API, for example:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(b'id,name\n1,english\n2,german', format='csv')
pprint(resource.to_view())
```
```
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | 'german'  |
+----+-----------+
```

## Writing Data

A similiar approach can be used for writing:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(scheme='buffer', format='csv')
print(target)
print(target.read_rows())
```
```
{'format': 'csv', 'scheme': 'buffer'}
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | 'german'  |
+----+-----------+
```

## Configuring Data

There are no options available for `BufferControl`.

References:
- [Buffer Control](../../references/schemes-reference.md#buffer)
