---
title: Pipeline Guide
---

A pipeline is a metadata object having one of these types:
- resource
- package
- others (depending on custom plugins you use)

## Creating Pipeline

For resource and package types it's basically the same functionality as we have seen above but written declaratively. So let's just run the same resource transformation as we did in the `Tranforming Resource` section:

```python title="Python"
from pprint import pprint
from frictionless import Pipeline, transform, steps

pipeline = Pipeline({
    'type': 'resource',
    'source': {'path': 'data/transform.csv'},
    'steps': [
        {'code': 'table-normalize'},
        {'code': 'table-melt', field_name: 'name'}
    ]
})
```

## Validating Pipeline

Let's run this pipeline:

```python title="Python"
status = transform(pipeline)
pprint(status.task.target.schema)
pprint(status.task.target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'variable'},
            {'name': 'value'}]}
[Row([('name', 'germany'), ('variable', 'id'), ('value', 1)]),
 Row([('name', 'germany'), ('variable', 'population'), ('value', 83)]),
 Row([('name', 'france'), ('variable', 'id'), ('value', 2)]),
 Row([('name', 'france'), ('variable', 'population'), ('value', 66)]),
 Row([('name', 'spain'), ('variable', 'id'), ('value', 3)]),
 Row([('name', 'spain'), ('variable', 'population'), ('value', 47)])]
```
