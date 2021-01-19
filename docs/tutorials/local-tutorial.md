---
title: Local Data Tutorial
---

:::tip Status
Plugin: **STABLE**
:::

You can read and write files locally with Frictionless. It's basic functionality.

## Reading Local Data

You can read using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='data/table.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Local Data

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv')
```

```bash
!cat tmp/table.csv
```


## Configuring Local Data

There are no options available in `LocalControl`.

References:
- [Local Control](https://frictionlessdata.io/tooling/python/controls-reference/#local)
