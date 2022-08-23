# Table Checks

## Table Dimensions

This check is used to validate if your data has expected dimensions as: exact number of rows , minimum and maximum number of rows, exact number of fields , minimum and maximum  number of fields.

### Basic Example

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]
report = validate(source, checks=[checks.table_dimensions(num_rows=5)])
pprint(report.flatten(["type", "message"]))
```

### Multiple Limits

You can also give multiples limits at the same time:

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]
report = validate(source, checks=[checks.table_dimensions(num_rows=5, num_fields=4)])
pprint(report.flatten(["type", "message"]))
```

### Using Declaratively

It is possible to use de check declaratively as:

```python script tabs=Python
from pprint import pprint
from frictionless import Check, validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]

check = Check.from_descriptor({"type": "table-dimensions", "minFields": 4, "maxRows": 3})
report = validate(source, checks=[check])
pprint(report.flatten(["type", "message"]))
```

But the table dimensions check arguments `num_rows`, `min_rows`, `max_rows`, `num_fields`, `min_fields`, `max_fields` must be passed in camelCase format as the example above i.e. `numRows`, `minRows`, `maxRows`, `numFields`, `minFields` and `maxFields`.

### Reference

```yaml reference
level: 4
references:
  - frictionless.checks.table_dimensions
```
