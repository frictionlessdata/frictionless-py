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

```yaml reference
level: 4
references:
  - frictionless.describe
```

## Extract

Extract is a high-level function (action) to read tabular data from a data source. The output is encoded in 'utf-8' scheme.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import extract

rows = extract('table.csv')
pprint(rows)
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.extract
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

```yaml reference
level: 4
references:
  - frictionless.validate
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

```yaml reference
level: 4
references:
  - frictionless.transform
```
