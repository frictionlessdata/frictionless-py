---
script:
  basepath: data
---

# Cell Steps

The Cell steps are responsible for cell operations like converting, replacing, or formating, along with others.

## Convert Cells

Converts cell values of one or more fields using arbitrary functions, method
invocations or dictionary translations.

### Using Value

We can provide a value to be set as a value of all cells of this field. Take into account that the value type needs to conform to the field type otherwise it will lead to a validation error:

```python script tabs=Python
from frictionless import Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_convert(field_name='population', value="100"),
    ],
)
print(target.to_view())
```

### Using Mapping

Another option to modify the field's cell is to provide a mapping. It's a translation table that uses literal matching to replace values. It's usually used for string fields:

```python script tabs=Python
from frictionless import Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_convert(field_name='name', mapping = {'germany': 'GERMANY'}),
    ],
)
print(target.to_view())
```

### Using Function

```markdown remark type=info
Functions are not supported in declarative pipelines
```

We can provide an arbitrary function to update the field cells. If you want to modify a non-string field it's really important to normalize the table first otherwise the function will be applied to a non-parsed value:

```python script tabs=Python
from frictionless import Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.cell_convert(field_name='population', function=lambda v: v*2),
    ],
)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.cell_convert
```

## Fill Cells

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_replace(pattern="france", replace=None),
        steps.cell_fill(field_name="name", value="FRANCE"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.cell_fill
```

## Format Cells

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_format(template="Prefix: {0}", field_name="name"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.cell_format
```

## Interpolate Cells

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_interpolate(template="Prefix: %s", field_name="name"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.cell_interpolate
```

## Replace Cells

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_replace(pattern="france", replace="FRANCE"),
    ]
)
print(target.schema)
print(target.to_view())
```

```yaml reference
level: 4
references:
  - frictionless.steps.cell_replace
```

## Set Cells

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
          steps.cell_set(field_name="population", value=100),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.cell_set
```
