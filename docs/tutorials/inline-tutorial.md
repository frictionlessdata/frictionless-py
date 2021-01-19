---
title: Inline Data Tutorial
---

:::tip Stability
Plugin: **STABLE**
:::

Frictionless supports parsing Inline Data.

```bash
! cat data/table.csv
```


## Reading Inline Data

You can read data in this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', 'german')])]


## Writing Inline Data

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write(format='inline')
```




    [['id', 'name'], [1, 'english'], [2, '中国人']]



## Configuring Inline Data

There is a dialect to configure this format, for example:


```python
from frictionless import Resource
from frictionless.plugins.inline import InlineDialect

dialect = InlineDialect(keyed=True, keys=['name', 'id'])
resource = Resource(data=[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}], dialect=dialect)
print(resource.read_rows())
```

    [Row([('name', 'english'), ('id', 1)]), Row([('name', 'german'), ('id', 2)])]


References:
- [Inline Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#inline)
