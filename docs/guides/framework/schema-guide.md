---
title: Schema Guide
---

> This guide in under development. We are moving some shared Schema information from describe, extract, validate, and transform guides to this guide.

## Schema Options

By default, a schema for a table is inferred under the hood but we can also pass it explicitly.

### Schema

The most common way is providing a schema argument to the Table constructor. For example, let's make the `id` field be a string instead of an integer:


```python
from frictionless import Table, Schema, Field

schema = Schema(fields=[Field(name='id', type='string'), Field(name='name', type='string')])
with Table('data/capital-3.csv', schema=schema) as table:
  pprint(table.schema)
  pprint(table.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'string'},
                {'name': 'name', 'type': 'string'}]}
    [Row([('id', '1'), ('name', 'London')]),
     Row([('id', '2'), ('name', 'Berlin')]),
     Row([('id', '3'), ('name', 'Paris')]),
     Row([('id', '4'), ('name', 'Madrid')]),
     Row([('id', '5'), ('name', 'Rome')])]

