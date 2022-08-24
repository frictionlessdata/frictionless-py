---
script:
  basepath: data
---

# Csv Format

CSV is a file format which you can you in Frictionless for reading and writing. Arguable it's the main Open Data format so it's supported very well in Frictionless.

## Reading Data

You can read this format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource('table.csv')
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table-output.csv')
print(target)
print(target.to_view())
```

## Configuration

There is a control to configure how Frictionless read and write files in this format. For example:

```python script tabs=Python
from frictionless import Resource, formats

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv', control=formats.CsvControl(delimiter=';'))
```

## Reference

```yaml reference
references:
  - frictionless.formats.CsvControl
```
