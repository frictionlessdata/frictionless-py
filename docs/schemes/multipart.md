---
script:
  basepath: data
---

# Multipart Scheme

You can read and write files split into chunks with Frictionless.

## Reading Data

You can read using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='chunk1.csv', extrapaths=['chunk2.csv'])
pprint(resource.read_rows())
```

## Writing Data

A similiar approach can be used for writing:

```python tabs=Python
from frictionless import Resource

resource = Resource(path='table.json')
resource.write('table{number}.json', scheme="multipart", control={"chunkSize": 1000000})
```

## Configuration

There is a `Control` to configure how Frictionless reads files using this scheme. For example:

```python tabs=Python
from frictionless import Resource
from frictionless.plugins.multipart import MultipartControl

control = MultipartControl(chunk_size=1000000)
resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table{number}.json', scheme="multipart", control=control)
```

## Reference

```yaml reference
references:
  - frictionless.schemes.MultipartControl
```
