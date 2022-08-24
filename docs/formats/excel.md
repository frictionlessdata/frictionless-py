---
script:
  basepath: data
---

# Excel Format

Excel is a very popular tabular data format that usually has `xlsx` (newer) and `xls` (older) file extensions. Frictionless supports Excel files extensively.

```bash tabs=CLI
pip install frictionless[excel]
pip install 'frictionless[excel]' # for zsh shell
```

## Reading Data

You can read this format using `Package/Resource`, for example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource(path='table.xlsx')
pprint(resource.read_rows())
```

## Writing Data

The same is actual for writing:

```python tabs=Python
from frictionless import Resource

source = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
target = source.write('table-output.xlsx')
print(target)
print(target.to_view())
```

## Configuration

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python tabs=Python
from frictionless import Resource, formats

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table-output-sheet.xls', control=formats.ExcelControl(sheet='My Table'))
```

## Reference

```yaml reference
references:
  - frictionless.formats.ExcelControl
```
