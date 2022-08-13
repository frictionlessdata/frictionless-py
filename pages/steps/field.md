# Field Steps

The Field steps are responsible for managing a Table Schema's fields. You can add or remove them along with more complex operations like unpacking.

## Add Field

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_add(name="note", type="string", value="eu"),
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
+----+-----------+------------+------+
| id | name      | population | note |
+====+===========+============+======+
|  1 | 'germany' |         83 | 'eu' |
+----+-----------+------------+------+
|  2 | 'france'  |         66 | 'eu' |
+----+-----------+------------+------+
|  3 | 'spain'   |         47 | 'eu' |
+----+-----------+------------+------+
```

## Filter Fields

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_filter(names=["id", "name"]),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'}]}
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'germany' |
+----+-----------+
|  2 | 'france'  |
+----+-----------+
|  3 | 'spain'   |
+----+-----------+
```

## Move Field

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_move(name="id", position=3),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'id', 'type': 'integer'}]}
+-----------+------------+----+
| name      | population | id |
+===========+============+====+
| 'germany' |         83 |  1 |
+-----------+------------+----+
| 'france'  |         66 |  2 |
+-----------+------------+----+
| 'spain'   |         47 |  3 |
+-----------+------------+----+
```

## Remove Field

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_remove(names=["id"]),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+-----------+------------+
| name      | population |
+===========+============+
| 'germany' |         83 |
+-----------+------------+
| 'france'  |         66 |
+-----------+------------+
| 'spain'   |         47 |
+-----------+------------+
```

## Split Field

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_split(name="name", to_names=["name1", "name2"], pattern="a"),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'name1', 'type': 'string'},
            {'name': 'name2', 'type': 'string'}]}
+----+------------+--------+-------+
| id | population | name1  | name2 |
+====+============+========+=======+
|  1 |         83 | 'germ' | 'ny'  |
+----+------------+--------+-------+
|  2 |         66 | 'fr'   | 'nce' |
+----+------------+--------+-------+
|  3 |         47 | 'sp'   | 'in'  |
+----+------------+--------+-------+
```

## Unpack Field

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", type="array", value=[1, 1]),
        steps.field_unpack(name="id", to_names=["id2", "id3"]),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'id2'},
            {'name': 'id3'}]}
+-----------+------------+-----+-----+
| name      | population | id2 | id3 |
+===========+============+=====+=====+
| 'germany' |         83 |   1 |   1 |
+-----------+------------+-----+-----+
| 'france'  |         66 |   1 |   1 |
+-----------+------------+-----+-----+
| 'spain'   |         47 |   1 |   1 |
+-----------+------------+-----+-----+
```

## Update Field

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", type="string", value=str),
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'string'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+------+-----------+------------+
| id   | name      | population |
+======+===========+============+
| None | 'germany' |         83 |
+------+-----------+------------+
| None | 'france'  |         66 |
+------+-----------+------------+
| None | 'spain'   |         47 |
+------+-----------+------------+
```
