---
script:
  basepath: data
---

# Ods Format

Frictionless supports ODS parsing.

```bash tabs=CLI
pip install frictionless[ods]
pip install 'frictionless[ods]' # for zsh shell
```

## Reading Data

You can read this format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='table.ods')
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python tabs=Python
from pprint import pprint
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table-output.ods')
pprint(target)
```

## Configuration

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python tabs=Python
from frictionless import Resource, formats

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table-output-sheet.ods', control=formats.OdsControl(sheet='My Table'))
```

## Reference

```yaml reference
references:
  - frictionless.formats.OdsControl
```
