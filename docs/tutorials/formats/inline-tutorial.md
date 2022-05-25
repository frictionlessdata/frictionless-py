---
title: Inline Tutorial
sidebar_label: Inline
---

Frictionless supports working with Inline Data from memory.

## Reading Data

You can read data in this format using `Package/Resource`, for example:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}]
```

## Writing Data

The same is actual for writing:

```python script title="Python"
from frictionless import Resource

source = Resource('data/table.csv')
target = source.write(format='inline')
print(target)
print(target.to_view())
```
```
{'data': [['id', 'name'], [1, 'english'], [2, '中国人']], 'format': 'inline'}
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | '中国人'     |
+----+-----------+
```

## Configuring Data

There is a dialect to configure this format, for example:

```python script title="Python"
from frictionless import Resource
from frictionless.plugins.inline import InlineDialect

dialect = InlineDialect(keyed=True, keys=['name', 'id'])
resource = Resource(data=[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}], dialect=dialect)
print(resource.to_view())
```
```
+-----------+----+
| name      | id |
+===========+====+
| 'english' |  1 |
+-----------+----+
| 'german'  |  2 |
+-----------+----+
```

References:
- [Inline Dialect](../../references/formats-reference.md#inline)
