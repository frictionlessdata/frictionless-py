---
title: Pipeline Guide
---

A pipeline is a metadata object having one of these types:
- resource
- package
- others (depending on custom plugins you use)

## Creating Pipeline

For resource and package types it's basically the same functionality as we have seen above but written declaratively. So let's just run the same resource transformation as we did in the `Tranforming Resource` section:

```python script title="Python"
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

```python script title="Python"
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
