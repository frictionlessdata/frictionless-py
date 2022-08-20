---
script:
  basepath: data
---

# Row Steps

These steps are row-based including row filtering, slicing, and many more.

## Filter Rows

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

## Search Rows

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

## Slice Rows

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

## Sort Rows

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

## Split Rows

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

## Subset Rows

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

## Ungroup Rows

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

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=row_filter
name: frictionless.steps.row_filter
```

```yaml reference tabs=row_search
name: frictionless.steps.row_search
```

```yaml reference tabs=row_slice
name: frictionless.steps.row_slice
```

```yaml reference tabs=row_sort
name: frictionless.steps.row_sort
```

```yaml reference tabs=row_split
name: frictionless.steps.row_split
```

```yaml reference tabs=row_subset
name: frictionless.steps.row_subset
```

```yaml reference tabs=row_ungroup
name: frictionless.steps.row_ungroup
```
