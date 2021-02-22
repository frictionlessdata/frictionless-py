---
title: Error Guide
---

The Error class is a metadata with no behavior. It's used to describe an error that happened during Framework work or during the validation.

## Error Example

To create a custom error you basically just need to fill the required class fields:

```python title="Python"
class DuplicateRowError(RowError):
    code = "duplicate-row"
    name = "Duplicate Row"
    tags = ["#table", "#row"]
    template = "Row at position {rowPosition} is duplicated: {note}"
    description = "The row is duplicated."
```
