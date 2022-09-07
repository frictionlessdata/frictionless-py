---
script:
  basepath: data
---

# Schema Class

The Table Schema is a core Frictionless Data concept meaning a metadata information regarding tabular data source. You can read [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/) for more information.

## Creating Schema

Let's create a table schema:

```python script tabs=Python
from frictionless import Schema, fields, describe

schema = describe('table.csv', type='schema') # from a resource path
schema = Schema.from_descriptor('schema.json') # from a descriptor path
schema = Schema.from_descriptor({'fields': [{'name': 'id', 'type': 'integer'}]}) # from a descriptor
```

As you can see it's possible to create a schema providing different kinds of sources which will be detector to have some type automatically (e.g. whether it's a dict or a path). It's possible to make this step more explicit:

```python script tabs=Python
from frictionless import Schema, Field

schema = Schema(fields=[fields.StringField(name='id')]) # from fields
schema = Schema.from_descriptor('schema.json') # from a descriptor
```

## Describing Schema

The standard support some additional schema's metadata:

```python script tabs=Python
from frictionless import Schema, fields

schema = Schema(
    fields=[fields.StringField(name='id')],
    missing_values=['na'],
    primary_key=['id'],
    # foreign_keys
)
print(schema)
```

If you have created a schema, for example, from a descriptor you can access this properties:

```python script tabs=Python
from frictionless import Schema

schema = Schema.from_descriptor('schema.json')
print(schema.missing_values)
# and others
```

And edit them:

```python script tabs=Python
from frictionless import Schema

schema = Schema.from_descriptor('schema.json')
schema.missing_values.append('-')
# and others
print(schema)
```

## Field Management

The Schema class provides useful methods to manage fields:

```python script tabs=Python
from frictionless import Schema, fields

schema = Schema.from_descriptor('schema.json')
print(schema.fields)
print(schema.field_names)
schema.add_field(fields.StringField(name='new-name'))
field = schema.get_field('new-name')
print(schema.has_field('new-name'))
schema.remove_field('new-name')
```

## Saving Descriptor

As any of the Metadata classes the Schema class can be saved as JSON or YAML:

```python tabs=Python
from frictionless import Schema, fields
schema = Schema(fields=[fields.IntegerField(name='id')])
schema.to_json('schema.json') # Save as JSON
schema.to_yaml('schema.yaml') # Save as YAML
```

## Reading Cells

During the process of data reading a resource uses a schema to convert data:

```python script tabs=Python
from frictionless import Schema, fields

schema = Schema(fields=[fields.IntegerField(name='integer'), fields.StringField(name='string')])
cells, notes = schema.read_cells(['3', 'value'])
print(cells)
```

## Writing Cells

During the process of data writing a resource uses a schema to convert data:

```python script tabs=Python
from frictionless import Schema, fields

schema = Schema(fields=[fields.IntegerField(name='integer'), fields.StringField(name='string')])
cells, notes = schema.write_cells([3, 'value'])
print(cells)
```

## Creating Field

Let's create a field:

```python script tabs=Python
from frictionless import fields

field = fields.IntegerField(name='name')
print(field)
```

Usually we work with fields which were already created by a schema:

```python script tabs=Python
from frictionless import describe

resource = describe('table.csv')
field = resource.schema.get_field('id')
print(field)
```

## Field Types

Frictionless Framework supports all the [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#types-and-formats) field types along with an ability to create custom types.

For some types there are additional properties available:

```python script tabs=Python
from frictionless import describe

resource = describe('table.csv')
field = resource.schema.get_field('id') # it's an integer
print(field.bare_number)
```

See the complete reference at [Tabular Fields](../fields/any.html).

## Reading Cell

During the process of data reading a schema uses a field internally. If needed a user can convert their data using this interface:

```python script tabs=Python
from frictionless import fields

field = fields.IntegerField(name='name')
cell, note = field.read_cell('3')
print(cell)
```

## Writing Cell

During the process of data writing a schema uses a field internally. The same as with reading a user can convert their data using this interface:

```python script tabs=Python
from frictionless import fields

field = fields.IntegerField(name='name')
cell, note = field.write_cell(3)
print(cell)
```

## Reference

```yaml reference
references:
  - frictionless.Schema
  - frictionless.Field
```
