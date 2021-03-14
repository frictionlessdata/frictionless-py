---
title: Field Guide
---

Field is a lower level object that helps describe and convert tabular data.

## Creating Field

Let's create a field:

```python goodread title="Python"
from frictionless import Field

field = Field(name='name', type='integer')
```

Usually we work with fields which were already created by a schema:

```python goodread title="Python"
from frictionless import describe

resource = describe('data/table.csv')
field = resource.schema.get_field('id')
```

## Field Types

Frictionless Framework supports all the [Table Schema Spec](https://specs.frictionlessdata.io/table-schema/#types-and-formats) field types along with an ability to create custom types.

For some types there are additional properties available:

```python goodread title="Python"
from frictionless import describe

resource = describe('data/table.csv')
field = resource.schema.get_field('id') # it's an integer
field.bare_number
```

## Reading Cell

During the process of data reading a schema uses a field internally. If needed a user can convert their data using this interface:

```python goodread title="Python"
from frictionless import Field

field = Field(name='name', type='integer')
field.read_cell('3') # 3
```

## Writing Cell

During the process of data writing a schema uses a field internally. The same as with reasing a user can convert their data using this interface:

```python goodread title="Python"
from frictionless import Field

field = Field(name='name', type='integer')
field.write_cell(3) # '3'
```
