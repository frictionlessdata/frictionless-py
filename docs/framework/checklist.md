# Checklist Class

## Creating Checklist

Checklist is a set of validation checks and a few addition settings. Let's create a checklist:

```python script tabs=Python
from frictionless import Checklist, checks

checklist = Checklist(checks=[checks.row_constraint(formula='id > 1')])
print(checklist)
```

## Validation Checks

The Check concept is a part of the Validation API. You can create a custom Check to be used as part of resource or package validation.

```python title="Python"
from frictionless import Check, errors

class duplicate_row(Check):
    code = "duplicate-row"
    Errors = [errors.DuplicateRowError]

    def __init__(self, descriptor=None):
        super().__init__(descriptor)
        self.__memory = {}

    def validate_row(self, row):
        text = ",".join(map(str, row.values()))
        hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        match = self.__memory.get(hash)
        if match:
            note = 'the same as row at position "%s"' % match
            yield errors.DuplicateRowError.from_row(row, note=note)
        self.__memory[hash] = row.row_position

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {},
    }
```

It's usual to create a custom [Error](../../docs/framework/classes.html) along side with a Custom Check.

## Reference

```yaml reference
references:
  - frictionless.Checklist
  - frictionless.Check
```
