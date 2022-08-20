---
script:
  basepath: data
---

# Other Classes

## Error

The Error class is a metadata with no behavior. It's used to describe an error that happened during Framework work or during the validation.

To create a custom error you basically just need to fill the required class fields:

```python title="Python"
from frictionless import errors

class DuplicateRowError(errors.RowError):
    code = "duplicate-row"
    name = "Duplicate Row"
    tags = ["#table", "#row", "#duplicate"]
    template = "Row at position {rowPosition} is duplicated: {note}"
    description = "The row is duplicated."
```

## Stats

The Stats represent various describe/validate stats:

```python script title="Python"
from frictionless import describe

resource = describe('table.csv', stats=True)
print(resource.stats)
```

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=Error
name: frictionless.Error
```

```yaml reference tabs=Stats
name: frictionless.Stats
```
