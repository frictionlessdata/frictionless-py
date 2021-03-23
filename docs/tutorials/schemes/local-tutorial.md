---
title: Local Tutorial
sidebar_label: Local
---

You can read and write files locally with Frictionless. It's basic functionality.

## Reading Local Data

You can read using `Package/Resource` or `Table` API, for example:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv')
print(resource.read_rows())
```
```
[Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]
```

## Writing Local Data

The same is actual for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv')
```

## Configuring Local Data

There are no options available in `LocalControl`.

References:
- [Local Control](../../references/schemes-reference.md#local)
