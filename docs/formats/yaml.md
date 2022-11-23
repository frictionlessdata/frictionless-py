---
script:
  basepath: data
---

# Json Format

Frictionless supports parsing YAML tables.

## Reading Data

> We use the `path` argument to ensure that it will not be guessed to be a metadata file

You can read this format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='table.yaml', type='table')
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(path='table-output.yaml', type='table')
print(target)
print(target.to_view())
```

## Configuration

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource, formats

control=formats.YamlControl(keyed=True)
resource = Resource(path='table.keyed.yaml', type='table', control=control)
pprint(resource.read_rows())
```

## Reference

```yaml reference
references:
  - frictionless.formats.YamlControl
```
