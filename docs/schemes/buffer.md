# Buffer Scheme

Frictionless supports working with bytes loaded into memory.

## Reading Data

You can read Buffer Data using `Package/Resource` API, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(b'id,name\n1,english\n2,german', format='csv')
pprint(resource.read_rows())
```

## Writing Data

A similiar approach can be used for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(scheme='buffer', format='csv')
print(target)
print(target.read_rows())
```
