---
title: Schema Guide
cleanup:
  - rm schema.json
  - rm schema.yaml
---

The Table Schema is a core Frictionless Data concept meaning a metadata information regarding tabular data source. You can read [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/) for more information.

## Creating Schema

Let's create a table schema:

```python script title="Python"
from frictionless import Schema, describe

schema = describe('data/table.csv', type='schema') # from a resource path
schema = Schema('data/schema.json') # from a descriptor path
schema = Schema({'fields': {'name': 'id', 'type': 'integer'}}) # from a descriptor
```

As you can see it's possible to create a schema providing different kinds of sources which will be detector to have some type automatically (e.g. whether it's a dict or a path). It's possible to make this step more explicit:

```python script title="Python"
from frictionless import Schema, Field

schema = Schema(fields=[Field(name='id', type='string')]) # from fields
schema = Schema(descriptor='data/schema.json') # from a descriptor
```

## Describing Schema

The specs support some additional schema's metadata:

```python script title="Python"
from frictionless import Schema, Resource

package = Schema(
    fields=[Field(name='id', type='string')],
    missing_values=['na'],
    primary_key=['id'],
    # foreign_keys
)
```

If you have created a schema, for example, from a descriptor you can access this properties:

```python script title="Python"
from frictionless import Schema

schema = Schema('data/schema.json')
schema.missing_values
schema.primary_key
# and others
```

And edit them:

```python script title="Python"
from frictionless import Schema

schema = Schema('data/schema.json')
schema.missing_values.append('-')
# and others
```

## Field Management

The Schema class provides useful methods to manage fields:

```python script title="Python"
from frictionless import Schema, Field

schema = Schema('data/schema.json')
print(schema.fields)
print(schema.field_names)
schema.add_field(Field(name='name', type='string'))
field = schema.get_field('name')
print(schema.has_field('name'))
schema.remove_field('name')
```
```
[{'name': 'id', 'type': 'integer'}, {'name': 'name', 'type': 'string'}]
['id', 'name']
True
```

## Saving Descriptor

As any of the Metadata classes the Schema class can be saved as JSON or YAML:

```python script title="Python"
from frictionless import Schema
schema = Schema(fields=[Field(name='id', type='integer')])
schema.to_json('schema.json') # Save as JSON
schema.to_yaml('schema.yaml') # Save as YAML
```

## Reading Cells

During the process of data reading a resource uses a schema to convert data:

```python script title="Python"
from frictionless import Schema, Field

schema = Schema(fields=[Field(type='integer'), Field(type='string')])
schema.read_cells(['3', 'value']) # [3, 'value']
```

## Writing Cells

During the process of data writing a resource uses a schema to convert data:

```python script title="Python"
from frictionless import Schema, Field

schema = Schema(fields=[Field(type='integer'), Field(type='string')])
schema.write_cells([3, 'value']) # ['3', 'value']
schema.write_cells([3, 'value'], types=['string']) # [3, 'value']
```
