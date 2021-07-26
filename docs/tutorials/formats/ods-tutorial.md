---
title: ODS Tutorial
sidebar_label: ODS
cleanup:
  - rm table.ods
---

Frictionless supports ODS parsing.

```bash title="CLI"
pip install frictionless[ods]
```

## Reading Data

You can read this format using `Package/Resource`, for example:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='data/table.ods')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

The same is actual for writing:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table.ods')
pprint(target)
```
```
{'path': 'table.ods'}
```

## Configuring ODS

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.ods import OdsDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.ods', dialect=OdsDialect(sheet='My Table'))
```

References:
- [ODS Dialect](../../references/formats-reference.md#ods)
