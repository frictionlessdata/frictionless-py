---
title: Pipeline Guide
---

A pipeline is a metadata object having one of these types:
- resource
- package
- others (depending on custom plugins you use)

## Creating Pipeline

For resource and package types it's basically the same functionality as we have seen above but written declaratively. So let's just run the same resource transformation as we did in the `Tranforming Resource` section:

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
```

## Running Pipeline

Let's run this pipeline:

```python goodread title="Python"
status = transform(pipeline)
pprint(status.task.target.schema)
pprint(status.task.target.read_rows())
```
```
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
