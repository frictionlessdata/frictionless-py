---
script:
  basepath: data
---

# Table Steps

These steps are meant to be used on a table level of a resource. This includes various different operations from simple validation or writing to the disc to complex re-shaping like pivoting or melting.

## Aggregate Table

Group rows under the given group_name then apply aggregation functions provided as aggregation dictionary (see example)

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform-groups.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_aggregate(
            group_name="name", aggregation={"sum": ("population", sum)}
        ),
    ],
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_aggregate
name: frictionless.steps.table_aggregate
level: 4
```

## Attach Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
      steps.table_attach(resource=Resource(data=[["note"], ["large"], ["mid"]])),
    ],
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_attach
name: frictionless.steps.table_attach
level: 4
```

## Debug Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
      steps.table_debug(function=print),
    ],
)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_debug
name: frictionless.steps.table_debug
level: 4
```

## Diff Tables

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_diff(
            resource=Resource(
                data=[
                    ["id", "name", "population"],
                    [1, "germany", 83],
                    [2, "france", 50],
                    [3, "spain", 47],
                ]
            )
        ),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_diff
name: frictionless.steps.table_diff
level: 4
```

## Intersect Tables

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_intersect(
            resource=Resource(
                data=[
                    ["id", "name", "population"],
                    [1, "germany", 83],
                    [2, "france", 50],
                    [3, "spain", 47],
                ]
            ),
        ),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_intersect
name: frictionless.steps.table_intersect
level: 4
```

## Join Tables

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_join(
            resource=Resource(data=[["id", "note"], [1, "beer"], [2, "vine"]]),
            field_name="id",
        ),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_join
name: frictionless.steps.table_join
level: 4
```

## Melt Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_melt(field_name="name"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_melt
name: frictionless.steps.table_melt
level: 4
```

## Merge Tables

### Example

```markdown remark type=danger
This functionality is currently disabled as being fixed in [#1221](https://github.com/frictionlessdata/frictionless-py/issues/1221)
```

```python tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_merge(
            resource=Resource(data=[["id", "name", "note"], [4, "malta", "island"]])
        ),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_merge
name: frictionless.steps.table_merge
level: 4
```

## Normalize Table

The `table_normalize` step normalizes an underlaying tabular stream (cast types and fix dimensions) according to a provided or inferred schema. If your data is not really big it's recommended to normalize a table before any others steps.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource("table.csv")
print(source.read_cells())
target = transform(
    source,
    steps=[
        steps.table_normalize(),
    ]
)
print(target.read_cells())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_normalize
name: frictionless.steps.table_normalize
level: 4
```

## Pivot Table

### Example

```markdown remark type=danger
This functionality is currently disabled as being fixed in [#1220](https://github.com/frictionlessdata/frictionless-py/issues/1220)
```

```python tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform-pivot.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_pivot(f1="region", f2="gender", f3="units", aggfun=sum),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_pivot
name: frictionless.steps.table_pivot
level: 4
```

## Print Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_print(),
    ]
)
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_print
name: frictionless.steps.table_print
level: 4
```

## Recast Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_melt(field_name="id"),
        steps.table_recast(field_name="id"),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_recast
name: frictionless.steps.table_recast
level: 4
```

## Transpose Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_transpose(),
    ]
)
print(target.schema)
print(target.to_view())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_transpose
name: frictionless.steps.table_transpose
level: 4
```

## Validate Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_set(field_name="population", value="bad"),
        steps.table_validate(),
    ]
)
pprint(target.schema)
try:
  pprint(target.to_view())
except Exception as exception:
  pprint(exception)
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_validate
name: frictionless.steps.table_validate
level: 4
```

## Write Table

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_write(path='transform.json'),
    ]
)
```

Let's read the output:

```bash script tabs=CLI
cat transform.json
```

```python script tabs=Python
with open('transform.json') as file:
    print(file.read())
```

### Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=table_write
name: frictionless.steps.table_write
level: 4
```
