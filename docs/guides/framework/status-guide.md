---
title: Status Guide
---

The Status class instance is a result of a Pipeline execution.

## Getting Status

We need to run a pipeline to get a status:

```python goodread title="Python"
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

```python goodread title="Python"
pprint(status.valid)
pprint(status.task.target.schema)
pprint(status.task.target.read_rows())
```
```
True
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'variable'},
            {'name': 'value'}]}
[{'name': 'germany', 'variable': 'id', 'value': 1},
 {'name': 'germany', 'variable': 'population', 'value': 83},
 {'name': 'france', 'variable': 'id', 'value': 2},
 {'name': 'france', 'variable': 'population', 'value': 66},
 {'name': 'spain', 'variable': 'id', 'value': 3},
 {'name': 'spain', 'variable': 'population', 'value': 47}]
```
