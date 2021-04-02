---
title: CSV Tutorial
sidebar_label: CSV
goodread:
  cleanup:
    - rm table.csv
---

CSV is a file format which you can you in Frictionless for reading and writing. Arguable it's the main Open Data format so it's supported very well in Frictionless.

## Reading Data

You can read this format using `Package/Resource`, for example:

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

## Configuring Data

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.csv import CsvDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv', dialect=CsvDialect(delimiter=';'))
```

References:
- [Csv Dialect](../../references/formats-reference.md#csv)
