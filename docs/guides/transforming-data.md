---
title: Transforming Data
---

Transforming data in Frictionless means modifying a data + metadata from the state A to the state B. For example, it can be a dirty Excel file we need to transform to a cleaned CSV file or a folder of data files we want to update and save as a data package.

For the core transform functions Frictionless uses amazing [PETL](https://petl.readthedocs.io/en/stable/) project under the hood. This library provides lazy-loading functionality in running data pipelines. On top of it Frictionless adds metadata management and a bridge between already familiar concepts like Pacakge/Resource and PETL's processors.

Frictionless supports a few different kinds of data and metadata transformations:
- resource and package transforms
- transforms based on a declarative pipeline

The main difference between the first two and pipelines that resource and package transforms are imperative while pipelines can be created beforehand or shared as a JSON file. Also, Frictionless supports a [Dataflows](https://frictionlessdata.io/tooling/python/working-with-dataflows/) pipeline runner. You need to install the `dataflows` plugin to use it.


```python
! cat data/transform.csv
```

    id,name,population
    1,germany,83
    2,france,66
    3,spain,47



```python
! cat data/transform-groups.csv
```

    id,name,population,year
    1,germany,83,2020
    2,germany,77,1920
    3,france,66,2020
    4,france,54,1920
    5,spain,47,2020
    6,spain,33,1920



```python
! cat data/transform-pivot.csv
```

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


## Transform Functions

The high-level interface for transforming data provided by Frictionless is a set of `transform` functions:
- `transform`: it will detect the source type and transform data accordingly
- `transform_resource`: it transforms a resource
- `transform_package`: it transforms a package
- `transform_pipeline`: it transforms resource or package based on a declarative pipeline definition

### Transforming Resource

Let's write our first transform. It's as easy as defining a source resource, applying transform steps and getting back a resulting target resource:


```python
from pprint import pprint
from frictionless import Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_melt(field_name="name"),
    ],
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'variable'},
                {'name': 'value'}]}
    [Row([('name', 'germany'), ('variable', 'id'), ('value', 1)]),
     Row([('name', 'germany'), ('variable', 'population'), ('value', 83)]),
     Row([('name', 'france'), ('variable', 'id'), ('value', 2)]),
     Row([('name', 'france'), ('variable', 'population'), ('value', 66)]),
     Row([('name', 'spain'), ('variable', 'id'), ('value', 3)]),
     Row([('name', 'spain'), ('variable', 'population'), ('value', 47)])]


Let's break the transforming steps we applied down:
1. `steps.table_normalize` - cast data types and shape the table according to the schema, inferred or provided
2. `steps.table_melt` - melt the table as it's done in R-Language or in other scientific libraries like `pandas`

There are dozens of other available steps that will be covered below.

### Transforming Package

Transforming a package is not much more difficult than a resource. Basically, a package is a set of resources so we will be transforming resources exactly the same way as we did above + we will be managing the resources list itself, adding or removing them:


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="data/transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='data/transform.csv'),
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

    ['main']
    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


The exact transformation we have applied actually doesn't make any sense as we just duplicated every row of the `main` resource. But it must have provided basic understanding of how simple and at the same time flexible package transformations can be.

### Transforming Pipeline

A pipeline is a metadata object having one of these types:
- resource
- package
- dataflows
- others (depending on custom plugins you use)

For resource and package types it's basically the same functionality as we have seen above but written declaratively. So let's just run the same resource transformation as we did in the `Tranforming Resource` section:


```python
from pprint import pprint
from frictionless import Pipeline, transform, steps

pipeline = Pipeline({
    'type': 'resource',
    'source': {'path': 'data/transform.csv'},
    'steps': [
        {'type': 'tableNormalize', 'spec': {}},
        {'type': 'tableMelt', 'spec': {'fieldName': 'name'}}
    ]
})
target = transform(pipeline)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'variable'},
                {'name': 'value'}]}
    [Row([('name', 'germany'), ('variable', 'id'), ('value', 1)]),
     Row([('name', 'germany'), ('variable', 'population'), ('value', 83)]),
     Row([('name', 'france'), ('variable', 'id'), ('value', 2)]),
     Row([('name', 'france'), ('variable', 'population'), ('value', 66)]),
     Row([('name', 'spain'), ('variable', 'id'), ('value', 3)]),
     Row([('name', 'spain'), ('variable', 'population'), ('value', 47)])]


And as we had expected we got the same result.

## Transform Options

The `transorm` function accepts the `source` argument which can be a resource, a package or a pipeline descriptor

### Resource

The `transform_resource` function also accepts:

- `steps` argument to define which steps should be applied on the source resource.

### Package

The `transform_package` function also accepts:

- `steps` argument to define which steps should be applied on the source package.

### Pipeline

The `transform_pipeline` function doesn't accept any additional arguments.

## Transform Principles

Frictionless Transforms bases on a few core principles which is shared with other parts of the framework:

### Conceptual Simplicity

Frictionless Transforms is not more than a list of functions that accept a source resource/package object and return a target resource/package object. Every function just updates the input's metadata and data and that's it. Thanks to this simplicity even a non-technical user can read the [source code](https://github.com/frictionlessdata/frictionless-py/blob/7ad8e692ad00131cdc9fa51258d8b860c62e77bc/frictionless/transform/resource.py#L7) of the transform function and understand how it works. And understanding the tools you use can be really important for mastering them.

### Metadata Matters

There is plenty of great ETL-frameworks written in Python and other languages. As said, we use one of them (PETL) under the hood. The core difference between Frictionless and others that we treat metadata as a first-class citizen. It means that you don't loose type and other important information during the pipeline evaluation.

### Data Streaming

Whenever it's possible Frictionless streams the data instead of reading it into memory. For example, for sorting big tables we use a memory usage threshold and it's met we use file system to unload the data. Ability to stream the data give users power to work with files of any size.

### Lazy Evaluation

Unlike to systems like `Data Package Pipelines` core Frictionless Transforms doesn't have a back-pressured flow as all data manipulation happen on-demand. For example, if you transform a data package containing 10 big csv files but you only need to reshape one table Frictionless will not even read other tables. Actually, when you call `target = transform(source)` it does almost nothing until the data reading call like `target.read_rows()` is made.

### Lean Processing

Similar to the section above, Frictionless tries to be as much explicit as possible regarding actions taken. For example, it will not use CPU resources to cast data unless a user adds a "normalize", "validate" or similar steps. So it's possible to transform rather big file without even casting types, for example, if you just need to reshape it.

## Transform Steps

Frictionless includes more than 40+ builtin transform steps. They are grouped by the object so you can find them easily if you have code auto completion. Start typing, for example, `steps.table...` and you will see all the available steps. The groups are listed below and you will find every group described in more detail in the next sections. It's also possible to write custom transform steps. Please read the section below to learn more about it.

- resource
- table
- field
- row
- cell

## Resource Steps

### Add Resource


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="data/transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='data/transform.csv'),
    ],
)
pprint(target.resource_names)
pprint(target.get_resource('extra').schema)
pprint(target.get_resource('extra').read_rows())
```

    ['main', 'extra']
    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Remove Resource


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="data/transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_remove(name='main'),
    ],
)
pprint(target)
```

    {'profile': 'data-package', 'resources': []}


### Transform Resource


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="data/transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', path='data/transform.csv'),
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

    ['main']
    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Update Resource


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="data/transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_update(name='main', title='Main Resource', description='For the docs'),
    ],
)
pprint(target.get_resource('main'))
```

    {'compression': 'no',
     'compressionPath': '',
     'control': {'newline': ''},
     'description': 'For the docs',
     'dialect': {},
     'encoding': 'utf-8',
     'format': 'csv',
     'hashing': 'md5',
     'name': 'main',
     'path': 'data/transform.csv',
     'profile': 'tabular-data-resource',
     'query': {},
     'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                           {'name': 'name', 'type': 'string'},
                           {'name': 'population', 'type': 'integer'}]},
     'scheme': 'file',
     'title': 'Main Resource'}


## Table Steps

### Aggregate Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform-groups.csv")
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

    {'fields': [{'name': 'name', 'type': 'string'}, {'name': 'sum'}]}
    [Row([('name', 'france'), ('sum', 120)]),
     Row([('name', 'germany'), ('sum', 160)]),
     Row([('name', 'spain'), ('sum', 80)])]


### Attach Tables


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
      steps.table_attach(resource=Resource(data=[["note"], ["large"], ["mid"]])),
    ],
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'note', 'type': 'string'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83), ('note', 'large')]),
     Row([('id', 2), ('name', 'france'), ('population', 66), ('note', 'mid')]),
     Row([('id', 3), ('name', 'spain'), ('population', 47), ('note', None)])]


### Debug Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
      steps.table_debug(function=print),
    ],
)
pprint(target.read_rows())
```

    ['1', 'germany', '83']
    ['2', 'france', '66']
    ['3', 'spain', '47']
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Diff Tables


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 2), ('name', 'france'), ('population', 66)])]


### Intersect Tables


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Join Tables


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'note', 'type': 'string'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83), ('note', 'beer')]),
     Row([('id', 2), ('name', 'france'), ('population', 66), ('note', 'vine')])]


### Melt Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'variable'},
                {'name': 'value'}]}
    [Row([('name', 'germany'), ('variable', 'id'), ('value', 1)]),
     Row([('name', 'germany'), ('variable', 'population'), ('value', 83)]),
     Row([('name', 'france'), ('variable', 'id'), ('value', 2)]),
     Row([('name', 'france'), ('variable', 'population'), ('value', 66)]),
     Row([('name', 'spain'), ('variable', 'id'), ('value', 3)]),
     Row([('name', 'spain'), ('variable', 'population'), ('value', 47)])]


### Merge Tables


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'note', 'type': 'string'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83), ('note', None)]),
     Row([('id', 2), ('name', 'france'), ('population', 66), ('note', None)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47), ('note', None)]),
     Row([('id', 4), ('name', 'malta'), ('population', None), ('note', 'island')])]


### Pivot Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform-pivot.csv")
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

    {'fields': [{'name': 'region', 'type': 'string'},
                {'name': 'boy', 'type': 'integer'},
                {'name': 'girl', 'type': 'integer'}]}
    [Row([('region', 'east'), ('boy', 33), ('girl', 29)]),
     Row([('region', 'west'), ('boy', 35), ('girl', 23)])]


### Print Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_print(),
    ]
)
```

    ==  =======  ==========
    id  name     population
    ==  =======  ==========
     1  germany          83
     2  france           66
     3  spain            47
    ==  =======  ==========



### Recast Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Transpose Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'germany', 'type': 'integer'},
                {'name': 'france', 'type': 'integer'},
                {'name': 'spain', 'type': 'integer'}]}
    [Row([('name', 'population'), ('germany', 83), ('france', 66), ('spain', 47)])]


### Validate Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    FrictionlessException('[step-error] The transfrom step has an error: "table_validate" raises "[type-error] The cell "bad" in row at position "2" and field "population" at position "3" has incompatible type: type is "integer/default""')


### Write Table


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.table_write(path='tmp/transform.json'),
    ]
)
```


```python
! cat tmp/transform.json
```

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

## Field Steps

### Add Field


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.field_add(name="note", type="string", value="eu"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'note', 'type': 'string'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83), ('note', 'eu')]),
     Row([('id', 2), ('name', 'france'), ('population', 66), ('note', 'eu')]),
     Row([('id', 3), ('name', 'spain'), ('population', 47), ('note', 'eu')])]


### Filter Fields


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.field_filter(names=["id", "name"]),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'}]}
    [Row([('id', 1), ('name', 'germany')]),
     Row([('id', 2), ('name', 'france')]),
     Row([('id', 3), ('name', 'spain')])]


### Move Field


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.field_move(name="id", position=3),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'id', 'type': 'integer'}]}
    [Row([('name', 'germany'), ('population', 83), ('id', 1)]),
     Row([('name', 'france'), ('population', 66), ('id', 2)]),
     Row([('name', 'spain'), ('population', 47), ('id', 3)])]


### Remove Field


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.field_remove(names=["id"]),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('name', 'germany'), ('population', 83)]),
     Row([('name', 'france'), ('population', 66)]),
     Row([('name', 'spain'), ('population', 47)])]


### Split Field


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.field_split(name="name", to_names=["name1", "name2"], pattern="a"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'name1', 'type': 'string'},
                {'name': 'name2', 'type': 'string'}]}
    [Row([('id', 1), ('population', 83), ('name1', 'germ'), ('name2', 'ny')]),
     Row([('id', 2), ('population', 66), ('name1', 'fr'), ('name2', 'nce')]),
     Row([('id', 3), ('population', 47), ('name1', 'sp'), ('name2', 'in')])]


### Unpack Field


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'id2'},
                {'name': 'id3'}]}
    [Row([('name', 'germany'), ('population', 83), ('id2', 1), ('id3', 1)]),
     Row([('name', 'france'), ('population', 66), ('id2', 1), ('id3', 1)]),
     Row([('name', 'spain'), ('population', 47), ('id2', 1), ('id3', 1)])]


### Update Field


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", type="string", value=str),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'string'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', '1'), ('name', 'germany'), ('population', 83)]),
     Row([('id', '2'), ('name', 'france'), ('population', 66)]),
     Row([('id', '3'), ('name', 'spain'), ('population', 47)])]


## Row Steps

### Filter Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.row_filter(predicat="<formula>id > 1"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Search Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.row_search(regex=r"^f.*"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 2), ('name', 'france'), ('population', 66)])]


### Slice Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.row_slice(head=2),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'france'), ('population', 66)])]


### Sort Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.row_sort(field_names=["name"]),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 2), ('name', 'france'), ('population', 66)]),
     Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Split Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.row_split(field_name="name", pattern="a"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germ'), ('population', 83)]),
     Row([('id', 1), ('name', 'ny'), ('population', 83)]),
     Row([('id', 2), ('name', 'fr'), ('population', 66)]),
     Row([('id', 2), ('name', 'nce'), ('population', 66)]),
     Row([('id', 3), ('name', 'sp'), ('population', 47)]),
     Row([('id', 3), ('name', 'in'), ('population', 47)])]


### Subset Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 1), ('name', 'france'), ('population', 66)]),
     Row([('id', 1), ('name', 'spain'), ('population', 47)])]


### Ungroup Rows


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform-groups.csv")
target = transform(
    source,
    steps=[
        steps.row_ungroup(group_name="name", selection="first"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'},
                {'name': 'year', 'type': 'integer'}]}
    [Row([('id', 3), ('name', 'france'), ('population', 66), ('year', 2020)]),
     Row([('id', 1), ('name', 'germany'), ('population', 83), ('year', 2020)]),
     Row([('id', 5), ('name', 'spain'), ('population', 47), ('year', 2020)])]


## Cell Steps

### Convert Cells


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_convert(value="n/a", field_name="name"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'n/a'), ('population', 83)]),
     Row([('id', 2), ('name', 'n/a'), ('population', 66)]),
     Row([('id', 3), ('name', 'n/a'), ('population', 47)])]


### Fill Cells


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
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

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'FRANCE'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Format Cells


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_format(template="Prefix: {0}", field_name="name"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'Prefix: germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'Prefix: france'), ('population', 66)]),
     Row([('id', 3), ('name', 'Prefix: spain'), ('population', 47)])]


### Interpolate Cells


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_interpolate(template="Prefix: %s", field_name="name"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'Prefix: germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'Prefix: france'), ('population', 66)]),
     Row([('id', 3), ('name', 'Prefix: spain'), ('population', 47)])]


### Replace Cells


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
        steps.cell_replace(pattern="france", replace="FRANCE"),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 83)]),
     Row([('id', 2), ('name', 'FRANCE'), ('population', 66)]),
     Row([('id', 3), ('name', 'spain'), ('population', 47)])]


### Set Cells


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="data/transform.csv")
target = transform(
    source,
    steps=[
          steps.cell_set(field_name="population", value=100),
    ]
)
pprint(target.schema)
pprint(target.read_rows())
```

    {'fields': [{'name': 'id', 'type': 'integer'},
                {'name': 'name', 'type': 'string'},
                {'name': 'population', 'type': 'integer'}]}
    [Row([('id', 1), ('name', 'germany'), ('population', 100)]),
     Row([('id', 2), ('name', 'france'), ('population', 100)]),
     Row([('id', 3), ('name', 'spain'), ('population', 100)])]


## Custom Steps

Here is an example of a custom step written as a python function:


```python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

def step(resource):
    with resource:
        resource.schema.remove_field("id")
        for row in resource.read_row_stream():
            del row["id"]
            yield row

source = Resource("data/transform.csv")
target = transform(source, steps=[step])
pprint(target.schema)
pprint(target.read_rows())
```

```
{'fields': [{'name': 'name', 'type': 'string'},
            {'name': 'population', 'type': 'integer'}]}
[Row([('name', 'germany'), ('population', 83)]),
 Row([('name', 'france'), ('population', 66)]),
 Row([('name', 'spain'), ('population', 47)])]
```

## Transform Utils

> Transform Utils is under construction

## Working with PETL

In some cases, it's better to use a lower-level API to achieve some goal. A resource can be exported as a PETL table. For more information please visit PETL's [documentation portal](https://petl.readthedocs.io/en/stable/).


```python
from frictionless import Resource

resource = Resource(path='data/transform.csv')
petl_table = resource.to_petl()
# Use it with PETL framework
print(petl_table)
```

    +---+---------+----+
    |   |         |    |
    +===+=========+====+
    | 1 | germany | 83 |
    +---+---------+----+
    | 2 | france  | 66 |
    +---+---------+----+
    | 3 | spain   | 47 |
    +---+---------+----+
