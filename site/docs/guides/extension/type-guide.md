---
title: Type Guide
---

Frictionless Framework support custom data types. A data type is an integer, float, or time. You can create your own time based on your domain model needs.

## Type Example

```python script title="Python"
from frictionless import Type

class ObjectType(Type):
    code = "object"
    constraints = [
        "required",
        "minLength",
        "maxLength",
        "enum",
    ]

    # Read

    def read_cell(self, cell):
        if not isinstance(cell, dict):
            if not isinstance(cell, str):
                return None
            try:
                cell = json.loads(cell)
            except Exception:
                return None
            if not isinstance(cell, dict):
                return None
        return cell

    # Write

    def write_cell(self, cell):
        return json.dumps(cell)
```
