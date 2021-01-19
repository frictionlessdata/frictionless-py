---
title: Filelike Data Tutorial
---

:::tip Stability
Plugin: **STABLE**
:::

Frictionless supports loading Filelike data.

## Reading Filelike Data

You can read Filelike using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

with open('data/table.csv', 'rb') as file:
  resource = Resource(path=file, format='csv')
  print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Filelike Data

The same is actual for writing CSV:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='filelike', format='csv')
```




    <_io.BufferedReader name='/tmp/tmplh6mlh54'>



## Configuring Filelike Data

There are no options available in `FilelikeControl`.

References:
- [Filelike Control](https://frictionlessdata.io/tooling/python/controls-reference/#filelike)
