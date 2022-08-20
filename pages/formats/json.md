---
script:
  basepath: data
---

# Json Format

Frictionless supports parsing JSON tables (JSON and JSONL/NDJSON).

```bash tabs=CLI
pip install frictionless[json]
pip install 'frictionless[json]' # for zsh shell
```

## Reading Data

> We use the `path` argument to ensure that it will not be guessed to be a metadata file

You can read this format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='table.json', type='table')
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python script tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write(path='table-output.json', type='table')
print(target)
print(target.to_view())
```

## Configuration

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource, formats

control=formats.JsonControl(keyed=True)
resource = Resource(path='table.keyed.json', type='table', control=control)
pprint(resource.read_rows())
```

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=JsonControl
name: frictionless.formats.JsonControl
```
