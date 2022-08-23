---
script:
  basepath: data
---

# Local Scheme

You can read and write files locally with Frictionless. This is a basic functionality of Frictionless.

## Reading Data

You can read using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='table.csv')
pprint(resource.read_rows())
```

## Writing Data

A similiar approach can be used for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table-output.csv')
print(target)
print(target.to_view())
```
