# Table Steps

These steps are meant to be used on a table level of a resource. This includes various different operations from simple validation or writing to the disc to complex re-shaping like pivoting or melting.

## Aggregate Table

Group rows under the given group_name then apply aggregation functions provided as aggregation dictionary (see example)

```python title="Python"
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
```
{'fields': [{'name': 'name', 'type': 'string'}, {'name': 'sum'}]}
+-----------+-----+
| name      | sum |
+===========+=====+
| 'france'  | 120 |
+-----------+-----+
| 'germany' | 160 |
+-----------+-----+
| 'spain'   |  80 |
+-----------+-----+
```

## Attach Tables

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
+----+-----------+------------+---------+
| id | name      | population | note    |
+====+===========+============+=========+
|  1 | 'germany' |         83 | 'large' |
+----+-----------+------------+---------+
|  2 | 'france'  |         66 | 'mid'   |
+----+-----------+------------+---------+
|  3 | 'spain'   |         47 | None    |
+----+-----------+------------+---------+

```

## Debug Table

```python title="Python"
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
```
{'id': 1, 'name': 'germany', 'population': 83}
{'id': 2, 'name': 'france', 'population': 66}
{'id': 3, 'name': 'spain', 'population': 47}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Diff Tables

```python title="Python"
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

## Intersect Tables

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Join Tables

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
+----+-----------+------------+--------+
| id | name      | population | note   |
+====+===========+============+========+
|  1 | 'germany' |         83 | 'beer' |
+----+-----------+------------+--------+
|  2 | 'france'  |         66 | 'vine' |
+----+-----------+------------+--------+
```

## Melt Table

```python title="Python"
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
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'variable'},
            {'name': 'value'}]}
+-----------+--------------+-------+
| name      | variable     | value |
+===========+==============+=======+
| 'germany' | 'id'         |     1 |
+-----------+--------------+-------+
| 'germany' | 'population' |    83 |
+-----------+--------------+-------+
| 'france'  | 'id'         |     2 |
+-----------+--------------+-------+
| 'france'  | 'population' |    66 |
+-----------+--------------+-------+
| 'spain'   | 'id'         |     3 |
+-----------+--------------+-------+
```

## Merge Tables

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
+----+-----------+------------+----------+
| id | name      | population | note     |
+====+===========+============+==========+
|  1 | 'germany' |         83 | None     |
+----+-----------+------------+----------+
|  2 | 'france'  |         66 | None     |
+----+-----------+------------+----------+
|  3 | 'spain'   |         47 | None     |
+----+-----------+------------+----------+
|  4 | 'malta'   | None       | 'island' |
+----+-----------+------------+----------+
```

## Normalize Table

The `table_normalize` step normalizes an underlaying tabular stream (cast types and fix dimensions) according to a provided or inferred schema. If your data is not really big it's recommended to normalize a table before any others steps.

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource("data/table.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
    ]
)
print(source.to_view())
print(target.to_view())
```
```
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | '中国人'     |
+----+-----------+

+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | '中国人'     |
+----+-----------+
```

## Pivot Table

```python title="Python"
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
```
{'fields': [{'name': 'region', 'type': 'string'},
            {'name': 'boy', 'type': 'integer'},
            {'name': 'girl', 'type': 'integer'}]}
+--------+-----+------+
| region | boy | girl |
+========+=====+======+
| 'east' |  33 |   29 |
+--------+-----+------+
| 'west' |  35 |   23 |
+--------+-----+------+
```

## Print Table

```python title="Python"
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
```
==  =======  ==========
id  name     population
==  =======  ==========
 1  germany          83
 2  france           66
 3  spain            47
==  =======  ==========
```

## Recast Table

```python title="Python"
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
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

## Transpose Table

```python title="Python"
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
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'germany', 'type': 'integer'},
            {'name': 'france', 'type': 'integer'},
            {'name': 'spain', 'type': 'integer'}]}
+--------------+-----------+----------+---------+
| id           | 1         | 2        | 3       |
+==============+===========+==========+=========+
| 'name'       | 'germany' | 'france' | 'spain' |
+--------------+-----------+----------+---------+
| 'population' |        83 |       66 |      47 |
+--------------+-----------+----------+---------+
```

## Validate Table

```python title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
FrictionlessException('[step-error] Step is not valid: "table_validate" raises "[type-error] Type error in the cell "bad" in row "2" and field "population" at position "3": type is "integer/default""')
```

## Write Table

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.table_write(path='tmp/transform.json'),
    ]
)
```


```bash
cat tmp/transform.json
```
```json title="Data: tmp/transform.json"
[
  [
    "id",
    "name",
    "population"
  ],
  [
    1,
    "germany",
    83
  ],
  [
    2,
    "france",
    66
  ],
  [
    3,
    "spain",
    47
  ]
]
```

```python
with open('tmp/transform.json') as file:
    print(file.read())
```
```json title="Data: tmp/transform.json"
[
  [
    "id",
    "name",
    "population"
  ],
  [
    1,
    "germany",
    83
  ],
  [
    2,
    "france",
    66
  ],
  [
    3,
    "spain",
    47
  ]
]
```
