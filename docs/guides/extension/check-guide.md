---
title: Check Guide
---

The Check concept is a part of the Validation API. You can create a custom Check to be used as part of resource or package validation.

## Check Example

```python goodread title="Python"
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

It's usuall to create a custom [Error](error-guide.md) along side with a Custom Check.
