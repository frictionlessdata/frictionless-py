---
script:
  basepath: data
---

# Pipeline Class

Pipeline is a object containg a list of transformation steps.

## Creating Pipeline

Let's create a pipeline using Python interface:

```python script tabs=Python
from frictionless import Pipeline, transform, steps

pipeline = Pipeline(steps=[steps.table_normalize(), steps.table_melt(field_name='name')])
print(pipeline)
```

## Running Pipeline

To run a pipeline you need to use a transform function or method:

```python script tabs=Python
from frictionless import Pipeline, transform, steps

pipeline = Pipeline(steps=[steps.table_normalize(), steps.table_melt(field_name='name')])
resource = transform('table.csv', pipeline=pipeline)
print(resource.schema)
print(resource.read_rows())
```

## Transform Steps

The Step concept is a part of the Transform API. You can create a custom Step to be used as part of resource or package transformation.

> This step uses PETL under the hood.

```python title="Python"
from frictionless import Step

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

## Reference

```yaml reference
references:
  - frictionless.Pipeline
  - frictionless.Step
```
