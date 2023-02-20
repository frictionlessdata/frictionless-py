---
script:
  basepath: data
---

# Spss Format

Frictionless supports reading and writing SPSS files.

```bash tabs=CLI
pip install frictionless[spss]
pip install 'frictionless[spss]' # for zsh shell
```

## Reading Data

You can read SPSS files:

```python tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource('table.sav')
pprint(resource.read_rows())
```

## Writing Data

You can write SPSS files:

```python tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table-output.sav')
pprint(target)
pprint(target.read_rows())
```
