---
script:
  basepath: data
---

# Inline Format

Frictionless supports working with Inline Data from memory.

## Reading Data

You can read data in this format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource('table.csv')
target = source.write(format='inline', datatype='table')
print(target)
print(target.to_view())
```

## Configuration

There is a dialect to configure this format, for example:

```python script tabs=Python
from frictionless import Resource, formats

control = formats.InlineControl(keyed=True, keys=['name', 'id'])
resource = Resource(data=[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}], control=control)
print(resource.to_view())
```

## Reference

```yaml reference
references:
  - frictionless.formats.InlineControl
```
