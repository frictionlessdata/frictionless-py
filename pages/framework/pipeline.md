# Pipeline Class

A pipeline is a metadata object having one of these types:
- resource
- package
- others (depending on custom plugins you use)

## Creating Pipeline

For resource and package types it's basically the same functionality as we have seen above but written declaratively. So let's just run the same resource transformation as we did in the `Tranforming Resource` section:

```python title="Python"
from frictionless import Pipeline, transform, steps

pipeline = Pipeline({
    'tasks': [
        {
            'type': 'resource',
            'source': {'path': 'data/transform.csv'},
            'steps': [
                {'code': 'table-normalize'},
                {'code': 'table-melt', 'fieldName': 'name'}
            ]
        }
    ]
})
```

## Running Pipeline

Let's run this pipeline:

```python title="Python"
status = transform(pipeline)
print(status.task.target.schema)
print(status.task.target.to_view())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'variable'},
            {'name': 'value'}]}
+----+-----------+------------+------+
| id | name      | population | cars |
+====+===========+============+======+
|  1 | 'germany' |         83 |  166 |
+----+-----------+------------+------+
|  2 | 'france'  |         66 |  132 |
+----+-----------+------------+------+
|  3 | 'spain'   |         47 |   94 |
+----+-----------+------------+------+
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

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=Pipeline
name: frictionless.Pipeline
```

```yaml reference tabs=Step
name: frictionless.Step
```
