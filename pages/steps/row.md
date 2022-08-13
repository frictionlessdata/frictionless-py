# Row Steps

These steps are row-based including row filtering, slicing, and many more.

## Filter Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+----------+------------+
| id | name     | population |
+====+==========+============+
|  2 | 'france' |         66 |
+----+----------+------------+
|  3 | 'spain'  |         47 |
+----+----------+------------+
```

## Search Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+----------+------------+
| id | name     | population |
+====+==========+============+
|  2 | 'france' |         66 |
+----+----------+------------+
```

## Slice Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
```

## Sort Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Split Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+--------+------------+
| id | name   | population |
+====+========+============+
|  1 | 'germ' |         83 |
+----+--------+------------+
|  1 | 'ny'   |         83 |
+----+--------+------------+
|  2 | 'fr'   |         66 |
+----+--------+------------+
|  2 | 'nce'  |         66 |
+----+--------+------------+
|  3 | 'sp'   |         47 |
+----+--------+------------+
```

## Subset Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  1 | 'france'  |         66 |
+----+-----------+------------+
|  1 | 'spain'   |         47 |
+----+-----------+------------+
```

## Ungroup Rows

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'year', 'type': 'integer'}]}
+----+-----------+------------+------+
| id | name      | population | year |
+====+===========+============+======+
|  3 | 'france'  |         66 | 2020 |
+----+-----------+------------+------+
|  1 | 'germany' |         83 | 2020 |
+----+-----------+------------+------+
|  5 | 'spain'   |         47 | 2020 |
+----+-----------+------------+------+
```
