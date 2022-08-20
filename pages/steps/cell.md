---
script:
  basepath: data
---

# Cell Steps

The Cell steps are responsible for cell operations like converting, replacing, or formating, along with others.

## Convert Cells

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_convert(value="n/a", field_name="name"),
    ]
)
print(target.schema)
print(target.to_view())
```

## Fill Cells

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

## Format Cells

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

## Interpolate Cells

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

## Replace Cells

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

## Set Cells

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

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=cell_convert
name: frictionless.steps.cell_convert
```

```yaml reference tabs=cell_fill
name: frictionless.steps.cell_fill
```

```yaml reference tabs=cell_format
name: frictionless.steps.cell_format
```

```yaml reference tabs=cell_interpolate
name: frictionless.steps.cell_interpolate
```

```yaml reference tabs=cell_replace
name: frictionless.steps.cell_replace
```

```yaml reference tabs=cell_set
name: frictionless.steps.cell_set
```
