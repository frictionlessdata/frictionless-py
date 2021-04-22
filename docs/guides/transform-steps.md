---
title: Transform Steps
goodread:
  prepare:
    - cp data/transform.csv transform.csv
    - cp data/transform-groups.csv transform-groups.csv
    - cp data/transform-pivot.csv transform-pivot.csv
  cleanup:
    - rm transform.csv
    - rm transform-groups.csv
    - rm transform-pivot.csv
---

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Frictionless includes more than 40+ built-in transform steps. They are grouped by the object so you can find them easily if you have code auto completion. Start typing, for example, `steps.table...` and you will see all the available steps. The groups are listed below and you will find every group described in more detail in the next sections. It's also possible to write custom transform steps. Please read the section below to learn more about it.  Let's prepare the data that we need to show how the checks below work:

> Download [`transform.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform.csv) to reproduce the examples (right-click and "Save link as").

```bash title="CLI"
cat transform.csv
```
```csv title="transform.csv"
id,name,population
1,germany,83
2,france,66
3,spain,47
```

> Download [`transform-groups.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform-groups.csv) to reproduce the examples (right-click and "Save link as").

```bash title="CLI"
cat transform-groups.csv
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

> Download [`transform-pivot.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform-pivot.csv) to reproduce the examples (right-click and "Save link as").

```bash title="CLI"
cat transform-pivot.csv
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

## Resource Steps

The Resource steps are only available for a package transformation. This includes some basic resource management operations like adding or removing resources along with the hierarchical `transform_resource` step.

### Add Resource

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='transform.csv'),
    ],
)
pprint(target.resource_names)
pprint(target.get_resource('extra').schema)
pprint(target.get_resource('extra').read_rows())
```
```
['main', 'extra']
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'france', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Remove Resource

```python goodread title="Python"
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

```python goodread title="Python"
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
pprint(target.resource_names)
pprint(target.get_resource('main').schema)
pprint(target.get_resource('main').read_rows())
```
```
['main']
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'france', 'population': 66},
 {'id': 2, 'name': 'france', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Update Resource

```python goodread title="Python"
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

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'}, {'name': 'sum'}]}
[{'name': 'france', 'sum': 120},
 {'name': 'germany', 'sum': 160},
 {'name': 'spain', 'sum': 80}]
```

### Attach Tables

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
      steps.table_attach(resource=Resource(data=[["note"], ["large"], ["mid"]])),
    ],
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
[{'id': 1, 'name': 'germany', 'population': 83, 'note': 'large'},
 {'id': 2, 'name': 'france', 'population': 66, 'note': 'mid'},
 {'id': 3, 'name': 'spain', 'population': 47, 'note': None}]
```

### Debug Table

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
      steps.table_debug(function=print),
    ],
)
pprint(target.read_rows())
```
```
{'id': 1, 'name': 'germany', 'population': 83}
{'id': 2, 'name': 'france', 'population': 66}
{'id': 3, 'name': 'spain', 'population': 47}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'france', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Diff Tables

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 2, 'name': 'france', 'population': 66}]
```

### Intersect Tables

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Join Tables

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
[{'id': 1, 'name': 'germany', 'population': 83, 'note': 'beer'},
 {'id': 2, 'name': 'france', 'population': 66, 'note': 'vine'}]
```

### Melt Table

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'variable'},
            {'name': 'value'}]}
[{'name': 'germany', 'variable': 'id', 'value': 1},
 {'name': 'germany', 'variable': 'population', 'value': 83},
 {'name': 'france', 'variable': 'id', 'value': 2},
 {'name': 'france', 'variable': 'population', 'value': 66},
 {'name': 'spain', 'variable': 'id', 'value': 3},
 {'name': 'spain', 'variable': 'population', 'value': 47}]
```

### Merge Tables

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
[{'id': 1, 'name': 'germany', 'population': 83, 'note': None},
 {'id': 2, 'name': 'france', 'population': 66, 'note': None},
 {'id': 3, 'name': 'spain', 'population': 47, 'note': None},
 {'id': 4, 'name': 'malta', 'population': None, 'note': 'island'}]
```

### Normalize Table

The `table_normalize` step normalizes an underlaying tabular stream (cast types and fix dimensions) according to a provided or inferred schema. If your data is not really big it's recommended to normalize a table before any others steps.

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource("data/table.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
    ]
)
pprint(source.read_lists())
pprint(target.read_lists())
```
```
[['id', 'name'], ['1', 'english'], ['2', '中国人']]
[['id', 'name'], [1, 'english'], [2, '中国人']]
```

### Pivot Table

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'region', 'type': 'string'},
            {'name': 'boy', 'type': 'integer'},
            {'name': 'girl', 'type': 'integer'}]}
[{'region': 'east', 'boy': 33, 'girl': 29},
 {'region': 'west', 'boy': 35, 'girl': 23}]
```

### Print Table

```python goodread title="Python"
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

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'france', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Transpose Table

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'germany', 'type': 'integer'},
            {'name': 'france', 'type': 'integer'},
            {'name': 'spain', 'type': 'integer'}]}
[{'name': 'population', 'germany': 83, 'france': 66, 'spain': 47}]
```

### Validate Table

```python goodread title="Python"
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
  pprint(target.read_rows())
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

```python goodread title="Python"
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

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_add(name="note", type="string", value="eu"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'note', 'type': 'string'}]}
[{'id': 1, 'name': 'germany', 'population': 83, 'note': 'eu'},
 {'id': 2, 'name': 'france', 'population': 66, 'note': 'eu'},
 {'id': 3, 'name': 'spain', 'population': 47, 'note': 'eu'}]
```

### Filter Fields

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_filter(names=["id", "name"]),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'}]}
[{'id': 1, 'name': 'germany'},
 {'id': 2, 'name': 'france'},
 {'id': 3, 'name': 'spain'}]
```

### Move Field

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_move(name="id", position=3),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'id', 'type': 'integer'}]}
[{'name': 'germany', 'population': 83, 'id': 1},
 {'name': 'france', 'population': 66, 'id': 2},
 {'name': 'spain', 'population': 47, 'id': 3}]
```

### Remove Field

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_remove(names=["id"]),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'name': 'germany', 'population': 83},
 {'name': 'france', 'population': 66},
 {'name': 'spain', 'population': 47}]
```

### Split Field

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_split(name="name", to_names=["name1", "name2"], pattern="a"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'name1', 'type': 'string'},
            {'name': 'name2', 'type': 'string'}]}
[{'id': 1, 'population': 83, 'name1': 'germ', 'name2': 'ny'},
 {'id': 2, 'population': 66, 'name1': 'fr', 'name2': 'nce'},
 {'id': 3, 'population': 47, 'name1': 'sp', 'name2': 'in'}]
```

### Unpack Field

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'id2'},
            {'name': 'id3'}]}
[{'name': 'germany', 'population': 83, 'id2': 1, 'id3': 1},
 {'name': 'france', 'population': 66, 'id2': 1, 'id3': 1},
 {'name': 'spain', 'population': 47, 'id2': 1, 'id3': 1}]
```

### Update Field

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", type="string", value=str),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'string'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': None, 'name': 'germany', 'population': 83},
 {'id': None, 'name': 'france', 'population': 66},
 {'id': None, 'name': 'spain', 'population': 47}]
```

## Row Steps

These steps are row-based including row filtering, slicing, and many more.

### Filter Rows

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 2, 'name': 'france', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Search Rows

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_search(regex=r"^f.*"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 2, 'name': 'france', 'population': 66}]
```

### Slice Rows

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_slice(head=2),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'france', 'population': 66}]
```

### Sort Rows

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_sort(field_names=["name"]),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 2, 'name': 'france', 'population': 66},
 {'id': 1, 'name': 'germany', 'population': 83},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Split Rows

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.row_split(field_name="name", pattern="a"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germ', 'population': 83},
 {'id': 1, 'name': 'ny', 'population': 83},
 {'id': 2, 'name': 'fr', 'population': 66},
 {'id': 2, 'name': 'nce', 'population': 66},
 {'id': 3, 'name': 'sp', 'population': 47},
 {'id': 3, 'name': 'in', 'population': 47}]
```

### Subset Rows

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 1, 'name': 'france', 'population': 66},
 {'id': 1, 'name': 'spain', 'population': 47}]
```

### Ungroup Rows

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform-groups.csv")
target = transform(
    source,
    steps=[
        steps.row_ungroup(group_name="name", selection="first"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'},
            {'name': 'year', 'type': 'integer'}]}
[{'id': 3, 'name': 'france', 'population': 66, 'year': 2020},
 {'id': 1, 'name': 'germany', 'population': 83, 'year': 2020},
 {'id': 5, 'name': 'spain', 'population': 47, 'year': 2020}]
```

## Cell Steps

The Cell steps are responsible for cell operations like converting, replacing, or formating, along with others.

### Convert Cells

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_convert(value="n/a", field_name="name"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'n/a', 'population': 83},
 {'id': 2, 'name': 'n/a', 'population': 66},
 {'id': 3, 'name': 'n/a', 'population': 47}]
```

### Fill Cells

```python goodread title="Python"
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
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'FRANCE', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Format Cells

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_format(template="Prefix: {0}", field_name="name"),
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

### Interpolate Cells

```python goodread title="Python"
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

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_replace(pattern="france", replace="FRANCE"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 83},
 {'id': 2, 'name': 'FRANCE', 'population': 66},
 {'id': 3, 'name': 'spain', 'population': 47}]
```

### Set Cells

```python goodread title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
          steps.cell_set(field_name="population", value=100),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```
```
{'fields': [{'name': 'id', 'type': 'integer'},
            {'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[{'id': 1, 'name': 'germany', 'population': 100},
 {'id': 2, 'name': 'france', 'population': 100},
 {'id': 3, 'name': 'spain', 'population': 100}]
```
