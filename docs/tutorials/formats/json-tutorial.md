---
title: JSON Tutorial
sidebar_label: JSON
cleanup:
  - rm table.json
---

Frictionless supports parsing JSON tables (JSON and JSONL/NDJSON).

```bash title="CLI"
pip install frictionless[json]
pip install 'frictionless[json]' # for zsh shell
```

## Reading Data

You can read this format using `Package/Resource`, for example:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='data/table.json')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

> We use the `path` argument for `resource.write` to ensure that it will not be guessed to be a metadata file

The same is actual for writing:

```python script title="Python"
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(path='table.json')
print(target)
print(target.to_view())
```
```
{'path': 'table.json'}
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | 'german'  |
+----+-----------+
```

## Configuring Data

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python title="Python"
from pprint import pprint
from frictionless import Resource
from frictionless.plugins.json import JsonDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.json', dialect=JsonDialect(keyed=True))
```

References:
- [JSON Dialect](../../references/formats-reference.md#json)
