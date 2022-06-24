---
title: Transform Steps
prepare:
  - cp data/transform.csv transform.csv
  - cp data/transform-groups.csv transform-groups.csv
  - cp data/transform-pivot.csv transform-pivot.csv
cleanup:
  - rm transform.csv
  - rm transform-groups.csv
  - rm transform-pivot.csv
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Frictionless includes more than 40+ built-in transform steps. They are grouped by the object so you can find them easily if you have code auto completion. Start typing, for example, `steps.table...` and you will see all the available steps. The groups are listed below and you will find every group described in more detail in the next sections. It's also possible to write custom transform steps. Please read the section below to learn more about it.  Let's prepare the data that we need to show how the checks below work:

> Download [`transform.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform.csv) to reproduce the examples (right-click and "Save link as").

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat transform.csv
```
```csv title="Data: transform.csv"
id,name,population
1,germany,83
2,france,66
3,spain,47
```

</TabItem>
<TabItem value="python">

```python script
with open('transform.csv') as file:
    print(file.read())
```
```csv title="transform.csv"
id,name,population
1,germany,83
2,france,66
3,spain,47
```

</TabItem>
</Tabs>

> Download [`transform-groups.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform-groups.csv) to reproduce the examples (right-click and "Save link as").

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat transform-groups.csv
```
```csv title="Data: transform-groups.csv"
id,name,population,year
1,germany,83,2020
2,germany,77,1920
3,france,66,2020
4,france,54,1920
5,spain,47,2020
6,spain,33,1920
```

</TabItem>
<TabItem value="python">

```python script
with open('transform-groups.csv') as file:
    print(file.read())
```
```csv title="transform-groups.csv"
id,name,population,year
1,germany,83,2020
2,germany,77,1920
3,france,66,2020
4,france,54,1920
5,spain,47,2020
6,spain,33,1920
```

</TabItem>
</Tabs>

> Download [`transform-pivot.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform-pivot.csv) to reproduce the examples (right-click and "Save link as").

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat transform-pivot.csv
```
```csv title="Data: transform-pivot.csv"
region,gender,style,units
east,boy,tee,12
east,boy,golf,14
east,boy,fancy,7
east,girl,tee,3
east,girl,golf,8
east,girl,fancy,18
west,boy,tee,12
west,boy,golf,15
west,boy,fancy,8
west,girl,tee,6
west,girl,golf,16
west,girl,fancy,1
```

</TabItem>
<TabItem value="python">

```python script
with open('transform-pivot.csv') as file:
    print(file.read())
```
```csv title="transform-pivot.csv"
region,gender,style,units
east,boy,tee,12
east,boy,golf,14
east,boy,fancy,7
east,girl,tee,3
east,girl,golf,8
east,girl,fancy,18
west,boy,tee,12
west,boy,golf,15
west,boy,fancy,8
west,girl,tee,6
west,girl,golf,16
west,girl,fancy,1
```

</TabItem>
</Tabs>

## Resource Steps

The Resource steps are only available for a package transformation. This includes some basic resource management operations like adding or removing resources along with the hierarchical `transform_resource` step.

### Add Resource

```python script title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='transform.csv'),
    ],
)
print(target.resource_names)
print(target.get_resource('extra').schema)
print(target.get_resource('extra').to_view())
```
```
['main', 'extra']
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

### Remove Resource

```python script title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_remove(name='main'),
    ],
)
pprint(target)
```
```
{'profile': 'data-package', 'resources': []}
```

### Transform Resource

```python script title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='transform.csv'),
        steps.resource_transform(name='main', steps=[
            steps.table_merge(resource='extra'),
            steps.row_sort(field_names=['id'])
        ]),
        steps.resource_remove(name="extra"),
    ],
)
print(target.resource_names)
print(target.get_resource('main').schema)
print(target.get_resource('main').to_view())
```
```
['main']
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  2 | 'france'  |         66 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

### Update Resource

```python script title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_update(name='main', title='Main Resource', description='For the docs'),
    ],
)
pprint(target.get_resource('main'))
```
```
{'description': 'For the docs',
 'encoding': 'utf-8',
 'format': 'csv',
 'hashing': 'md5',
 'name': 'main',
 'path': 'transform.csv',
 'profile': 'tabular-data-resource',
 'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                       {'name': 'name', 'type': 'string'},
                       {'name': 'population', 'type': 'integer'}]},
 'scheme': 'file',
 'title': 'Main Resource'}
```

## Table Steps

These steps are meant to be used on a table level of a resource. This includes various different operations from simple validation or writing to the disc to complex re-shaping like pivoting or melting.

### Aggregate Table

Group rows under the given group_name then apply aggregation functions provided as aggregation dictionary (see example)

```python script title="Python"
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

### Attach Tables

```python script title="Python"
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

### Debug Table

```python script title="Python"
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

### Diff Tables

```python script title="Python"
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

### Intersect Tables

```python script title="Python"
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

### Join Tables

```python script title="Python"
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

### Melt Table

```python script title="Python"
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

### Merge Tables

```python script title="Python"
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

### Normalize Table

The `table_normalize` step normalizes an underlaying tabular stream (cast types and fix dimensions) according to a provided or inferred schema. If your data is not really big it's recommended to normalize a table before any others steps.

```python script title="Python"
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

### Pivot Table

```python script title="Python"
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

### Print Table

```python script title="Python"
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

### Recast Table

```python script title="Python"
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

### Transpose Table

```python script title="Python"
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

### Validate Table

```python script title="Python"
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

### Write Table

```python script title="Python"
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

```bash title="CLI"
cat tmp/transform.json
```
```json title="tmp/transform.json"
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

## Field Steps

The Field steps are responsible for managing a Table Schema's fields. You can add or remove them along with more complex operations like unpacking.

### Add Field

```python script title="Python"
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

### Filter Fields

```python script title="Python"
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

### Move Field

```python script title="Python"
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

### Remove Field

```python script title="Python"
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

### Split Field

```python script title="Python"
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

### Unpack Field

```python script title="Python"
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

### Update Field

```python script title="Python"
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

### Merge Cells

```python script title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
     source,
     steps=[
     	 # seperator argument can be used to set delimeter. Default value is '-'
    	 # preserve argument keeps the original fields
         steps.field_merge(name="details", from_names=["name", "population"], preserve=True)
     ],
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'details', 'type': 'string'}]}
+----+-----------+------------+--------------+
| id | name      | population | details      |
+====+===========+============+==============+
|  1 | 'germany' |         83 | 'germany-83' |
+----+-----------+------------+--------------+
|  2 | 'france'  |         66 | 'france-66'  |
+----+-----------+------------+--------------+
|  3 | 'spain'   |         47 | 'spain-47'   |
+----+-----------+------------+--------------+
 ```


### Pack Cells

```python script title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
    	# field_type returns packed fields as JSON Object. Default value for field_type is 'array'
    	# preserve argument keeps the original fields
        steps.field_pack(name="details", from_names=["name", "population"], field_type="object", preserve=True)
    ]
)
print(target.schema)
print(target.to_view())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'details', 'type': 'object'}]}
+----+-----------+------------+-----------------------------------------+
| id | name      | population | details                                 |
+====+===========+============+=========================================+
|  1 | 'germany' |         83 | {'name': 'germany', 'population': '83'} |
+----+-----------+------------+-----------------------------------------+
|  2 | 'france'  |         66 | {'name': 'france', 'population': '66'}  |
+----+-----------+------------+-----------------------------------------+
|  3 | 'spain'   |         47 | {'name': 'spain', 'population': '47'}   |
+----+-----------+------------+-----------------------------------------+
```


## Row Steps

These steps are row-based including row filtering, slicing, and many more.

### Filter Rows

```python script title="Python"
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

### Search Rows

```python script title="Python"
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

### Slice Rows

```python script title="Python"
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

### Sort Rows

```python script title="Python"
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

### Split Rows

```python script title="Python"
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

### Subset Rows

```python script title="Python"
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

### Ungroup Rows

```python script title="Python"
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

## Cell Steps

The Cell steps are responsible for cell operations like converting, replacing, or formating, along with others.

### Convert Cells

```python script title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-------+------------+
| id | name  | population |
+====+=======+============+
|  1 | 'n/a' |         83 |
+----+-------+------------+
|  2 | 'n/a' |         66 |
+----+-------+------------+
|  3 | 'n/a' |         47 |
+----+-------+------------+
```

### Fill Cells

```python script title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |         83 |
+----+-----------+------------+
|  2 | 'FRANCE'  |         66 |
+----+-----------+------------+
|  3 | 'spain'   |         47 |
+----+-----------+------------+
```

### Format Cells

```python script title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-------------------+------------+
| id | name              | population |
+====+===================+============+
|  1 | 'Prefix: germany' |         83 |
+----+-------------------+------------+
|  2 | 'Prefix: france'  |         66 |
+----+-------------------+------------+
|  3 | 'Prefix: spain'   |         47 |
+----+-------------------+------------+
```

### Interpolate Cells

```python script title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'Prefix: germany', 'population': 83},
 {'id': 2, 'name': 'Prefix: france', 'population': 66},
 {'id': 3, 'name': 'Prefix: spain', 'population': 47}]
```

### Replace Cells

```python script title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-------------------+------------+
| id | name              | population |
+====+===================+============+
|  1 | 'Prefix: germany' |         83 |
+----+-------------------+------------+
|  2 | 'Prefix: france'  |         66 |
+----+-------------------+------------+
|  3 | 'Prefix: spain'   |         47 |
+----+-------------------+------------+
```

### Set Cells

```python script title="Python"
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
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
+----+-----------+------------+
| id | name      | population |
+====+===========+============+
|  1 | 'germany' |        100 |
+----+-----------+------------+
|  2 | 'france'  |        100 |
+----+-----------+------------+
|  3 | 'spain'   |        100 |
+----+-----------+------------+
```
