---
title: Excel Tutorial
sidebar_label: Excel
goodread:
  cleanup:
    - rm table.xlsx
---

Excel is a very popular tabular data format that usually has `xlsx` (newer) and `xls` (older) file extensions. Frictionless supports Excel files extensively.

```bash title="CLI"
pip install frictionless[excel]
```

## Reading Data

You can read this format using `Package/Resource`, for example:

```python goodread title="python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='data/table.xlsx')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

The same is actual for writing:

```python goodread title="python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table.xlsx')
pprint(target)
pprint(target.read_rows())
```
```
{'path': 'table.xlsx'}
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}]
```

## Configuring Data

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.excel import ExcelDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.xlsx', dialect=ExcelDialect(sheet='My Table'))
```

References:
- [Excel Dialect](../../references/formats-reference.md#excel)
