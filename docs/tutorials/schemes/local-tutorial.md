---
title: Local Tutorial
sidebar_label: Local
cleanup:
  - rm table.csv
---

You can read and write files locally with Frictionless. This is a basic functionality of Frictionless.

## Reading Data

You can read using `Package/Resource`, for example:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='data/table.csv')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

A similiar approach can be used for writing:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table.csv')
print(target)
print(target.to_view())
```
```
{'path': 'table.csv'}
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | 'german'  |
+----+-----------+
```

## Configuring Data

There are no options available for `LocalControl`.

References:
- [Local Control](../../references/schemes-reference.md#local)
