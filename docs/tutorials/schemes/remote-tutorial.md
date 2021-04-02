---
title: Remote Tutorial
sidebar_label: Remote
---

You can read files remotely with Frictionless. This is a basic functionality of Frictionless.

## Reading Remote Data

You can read using `Package/Resource`, for example:

```python title="Python"
from frictionless import Resource

resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv')
print(resource.read_rows())
```
```
[Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]
```

## Writing Remote Data

The same can be done for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('https://example.com/data/table.csv') # will POST the file to the server
```

## Configuring Remote Data

There is a `Control` to configure remote data, for example:

```python title="Python"
from frictionless import Resource
from frictionless.plugins.remote import RemoteControl

control = RemoteControl(http_timeout=10)
resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv', control=control)
print(resource.read_rows())
```
```
[Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]
```

References:
- [Remote Control](../../references/schemes-reference.md#remote)
