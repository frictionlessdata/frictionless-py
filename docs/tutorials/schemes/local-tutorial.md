---
title: Local Tutorial
sidebar_label: Local
goodread:
  cleanup:
    - rm table.csv
---

You can read and write files locally with Frictionless. It's basic functionality.

## Reading Data

You can read using `Package/Resource`, for example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='data/table.csv')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

The same is actual for writing:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table.csv')
pprint(target)
pprint(target.read_rows())
```
```
{'path': 'table.csv'}
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}]
```

## Using Control

There are no options available for `LocalControl`.

References:
- [Local Control](../../references/schemes-reference.md#local)
