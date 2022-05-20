---
title: Google Sheets Tutorial
sidebar_label: Google Sheets
---

> This functionality requires an experimental `gsheets` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports parsing Google Sheets data as a file format.

```bash title="CLI"
pip install frictionless[gsheets]
pip install 'frictionless[gsheets]' # for zsh shell
```

## Reading Data

You can read from Google Sheets using `Package/Resource`, for example:

```python script title="python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing')
print(resource.to_view())
```
```
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | '中国人'     |
+----+-----------+
```

## Writing Data

The same is actual for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write("https://docs.google.com/spreadsheets/d/<id>/edit", dialect={"credentials": ".google.json"})
```

## Configuring Data

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write("https://docs.google.com/spreadsheets/d/<id>/edit", dialect={"credentials": ".google.json"})
```

References:
- [Gseets Dialect](../../references/formats-reference.md#gsheets)
