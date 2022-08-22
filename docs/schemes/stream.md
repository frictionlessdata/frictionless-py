---
script:
  basepath: data
---

# Stream Scheme

Frictionless supports using data stored as File-Like objects in Python.

## Reading Data

> It's recommended to open files in byte-mode. If the file is opened in text-mode, Frictionless will try to re-open it in byte-mode.

You can read Stream using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

with open('table.csv', 'rb') as file:
  resource = Resource(file, format='csv')
  pprint(resource.read_rows())
```

## Writing Data

A similiar approach can be used for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(scheme='stream', format='csv')
print(target)
print(target.to_view())
```
