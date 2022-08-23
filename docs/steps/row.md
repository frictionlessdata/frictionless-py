---
script:
  basepath: data
---

# Row Steps

These steps are row-based including row filtering, slicing, and many more.

## Filter Rows

This step filters rows based on a provided formula or function.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.row_filter(formula="id > 1"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_filter
```

## Search Rows

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_search(regex=r"^f.*"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_search
```

## Slice Rows

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_slice(head=2),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_slice
```

## Sort Rows

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_sort(field_names=["name"]),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_sort
```

## Split Rows

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_split(field_name="name", pattern="a"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_split
```

## Subset Rows

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", value=1),
        steps.row_subset(subset="conflicts", field_name="id"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_subset
```

## Ungroup Rows

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform-groups.csv")
target = transform(
    source,
    steps=[
        steps.row_ungroup(group_name="name", selection="first"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.row_ungroup
```
