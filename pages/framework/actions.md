---
script:
  basepath: data
---

# Data Actions

## Describe

Describe is a high-level function (action) to infer a metadata from a data source.

### Example

```python script tabs=Python
from frictionless import describe

resource = describe('table.csv')
print(resource)
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=describe
name: frictionless.describe
level: 4
```

## Extract

Extract is a high-level function (action) to read tabular data from a data source.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import extract

rows = extract('table.csv')
pprint(rows)
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=extract
name: frictionless.extract
level: 4
```

## Validate

Validate is a high-level function (action) to validate data from a data source.

### Example

```python script tabs=Python
from frictionless import validate

report = validate('table.csv')
print(report.valid)
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=validate
name: frictionless.validate
level: 4
```

## Transform

Transform is a high-level function (action) to transform tabular data from a data source.

### Example

```python script tabs=Python
from frictionless import transform, steps

resource = transform('table.csv', steps=[steps.cell_set(field_name='name', value='new')])
print(resource.read_rows())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=transform
name: frictionless.transform
level: 4
```
