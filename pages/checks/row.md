# Row Checks

## Duplicate Row

This checks for duplicate rows. You need to take into account that checking for duplicate rows can lead to high memory consumption on big files. Here is an example:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = b"header\nvalue\nvalue"
report = validate(source, format="csv", checks=[checks.duplicate_row()])
pprint(report.flatten(["code", "message"]))
```
```
[['duplicate-row',
  'Row at position 3 is duplicated: the same as row at position "2"']]
```

## Row Constraint

This check is the most powerful one as it uses the external `simpleeval` package allowing you to evaluate arbitrary Python expressions on data rows. Let's show on an example:

```python title="Python"
from pprint import pprint
from frictionless import validate, checks

source = [
    ["row", "salary", "bonus"],
    [2, 1000, 200],
    [3, 2500, 500],
    [4, 1300, 500],
    [5, 5000, 1000],
]
report = validate(source, checks=[checks.row_constraint(formula="salary == bonus * 5")])
pprint(report.flatten(["code", "message"]))
```
```
[['row-constraint',
  'The row at position 4 has an error: the row constraint to conform is '
  '"salary == bonus * 5"']]
```
