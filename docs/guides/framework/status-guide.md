---
title: Status Guide
---

The Status class instance is a result of a Pipeline execution.

## Getting Status

We need to run a pipeline to get a status:

```python script title="Python"
from pprint import pprint
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
status = transform(pipeline)
```

## Exploring Status

Let's explore the execution status:

```python script title="Python"
print(status.valid)
print(status.task.target.schema)
print(status.task.target.to_view())
```
```
True
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'variable'},
            {'name': 'value'}]}
+-----------+--------------+-------+
| name      | variable     | value |
+===========+==============+=======+
| 'germany' | 'id'         |     1 |
+-----------+--------------+-------+
| 'germany' | 'population' |    83 |
+-----------+--------------+-------+
| 'france'  | 'id'         |     2 |
+-----------+--------------+-------+
| 'france'  | 'population' |    66 |
+-----------+--------------+-------+
| 'spain'   | 'id'         |     3 |
+-----------+--------------+-------+
```
