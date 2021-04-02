---
title: Remote Tutorial
sidebar_label: Remote
---

You can use remote files with Frictionless. It's basic functionality.

## Reading Data

You can read using `Package/Resource`, for example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

The same is actual for writing:

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('https://example.com/data/table.csv') # will POST the file to the server
```

## Using Control

There is a control to configure remote data, for example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource
from frictionless.plugins.remote import RemoteControl

control = RemoteControl(http_timeout=10)
resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv', control=control)
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

References:
- [Remote Control](../../references/schemes-reference.md#remote)
