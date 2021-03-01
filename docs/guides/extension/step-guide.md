---
title: Step Guide
---

The Step concept is a part of the Transform API. You can create a custom Step to be used as part of resource or package transformation.

## Step Example

> This step uses PETL under the hood.

```python title="Python"
class cell_set(Step):
    code = "cell-set"

    def __init__(self, descriptor=None, *, value=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    def transform_resource(self, resource):
        value = self.get("value")
        field_name = self.get("fieldName")
        yield from resource.to_petl().update(field_name, value)
```
