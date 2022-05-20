---
title: HTML Tutorial
sidebar_label: HTML
cleanup:
  - rm table.html
---

> This functionality requires an experimental `html` plugin. [Read More](../../references/plugins-reference.md)

Frictionless supports parsing HTML format:

```bash title="CLI"
pip install frictionless[html]
pip install 'frictionless[html]' # for zsh shell
```

## Reading Data

You can this file format using `Package/Resource`, for example:

```python script title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='data/table1.html')
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

```python script title="Python"
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table.html')
print(target)
print(target.to_view())
```
```
{'path': 'table.html'}
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | 'german'  |
+----+-----------+
```

## Configuring Data

There is a dialect to configure HTML, for example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.html import HtmlDialect

resource = Resource(path='data/table1.html', dialect=HtmlDialect(selector='#id'))
print(resource.read_rows())
```

References:
- [Html Dialect](../../references/formats-reference.md#html)
