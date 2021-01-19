---
title: Remote Data Tutorial
---

:::tip Stability
Plugin: **STABLE**
:::

You can read files remotely with Frictionless. It's basic functionality.

## Reading Remote Data

You can read using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Remote Data

The save is actual for writing:

```py
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('https://example.com/data/table.csv') # will POST the file to the server
```


## Configuring Remote Data

There is a control to configure remote data, for example:


```python
from frictionless import Resource
from frictionless.plugins.remote import RemoteControl

control = RemoteControl(http_timeout=10)
resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv', control=control)
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


References:
- [Remote Control](https://frictionlessdata.io/tooling/python/schemes-reference/#remote)
