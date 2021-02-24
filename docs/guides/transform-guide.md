---
title: Transform Guide
---

Transforming data in Frictionless means modifying a data + metadata from the state A to the state B. For example, it can be a dirty Excel file we need to transform to a cleaned CSV file or a folder of data files we want to update and save as a data package.

For the core transform functions Frictionless uses amazing [PETL](https://petl.readthedocs.io/en/stable/) project under the hood. This library provides lazy-loading functionality in running data pipelines. On top of it Frictionless adds metadata management and a bridge between already familiar concepts like Pacakge/Resource and PETL's processors.

Frictionless supports a few different kinds of data and metadata transformations:
- resource and package transforms
- transforms based on a declarative pipeline

The main difference between the first two and pipelines that resource and package transforms are imperative while pipelines can be created beforehand or shared as a JSON file. Also, Frictionless supports a [Dataflows](https://frictionlessdata.io/tooling/python/working-with-dataflows/) pipeline runner. You need to install the `dataflows` plugin to use it.

> Download [`transform.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform.csv) into the `data` folder to reproduce the examples

```bash title="CLI"
cat data/transform.csv
```
```csv title="data/transform.csv"
id,name,population
1,germany,83
2,france,66
3,spain,47
```

## Transform Functions

The high-level interface for transforming data provided by Frictionless is a set of `transform` functions:
- `transform`: it will detect the source type and transform data accordingly
- `transform_resource`: it transforms a resource
- `transform_package`: it transforms a package
- `transform_pipeline`: it transforms resource or package based on a declarative pipeline definition

## Transforming Resource

Let's write our first transform. It's as easy as defining a source resource, applying transform steps and getting back a resulting target resource:

```python title="Python"
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
```

Let's break the transforming steps we applied down:
1. `steps.table_normalize` - cast data types and shape the table according to the schema, inferred or provided
2. `steps.table_melt` - melt the table as it's done in R-Language or in other scientific libraries like `pandas`

There are dozens of other available steps that will be covered below.

## Transforming Package

Transforming a package is not much more difficult than a resource. Basically, a package is a set of resources so we will be transforming resources exactly the same way as we did above + we will be managing the resources list itself, adding or removing them:

```python title="Python"
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
```

The exact transformation we have applied actually doesn't make any sense as we just duplicated every row of the `main` resource. But it must have provided basic understanding of how simple and at the same time flexible package transformations can be.

## Transforming Pipeline

A pipeline is a metadata object having one of these types:
- resource
- package
- others (depending on custom plugins you use)

For resource and package types it's basically the same functionality as we have seen above but written declaratively. So let's just run the same resource transformation as we did in the `Tranforming Resource` section:

```python title="Python"
from pprint import pprint
from frictionless import Pipeline, transform, steps

pipeline = Pipeline({
    'type': 'resource',
    'source': {'path': 'data/transform.csv'},
    'steps': [
        {'code': 'table-normalize'},
        {'code': 'table-melt', field_name: 'name'}
    ]
})
target = transform(pipeline)
pprint(target.schema)
pprint(target.read_rows())
```
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
```

And as we had expected we got the same result.

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

## Available Steps

Frictionless includes more than 40+ builtin transform steps. They are grouped by the object so you can find them easily if you have code auto completion. Start typing, for example, `steps.table...` and you will see all the available steps. The groups are listed below and you will find every group described in more detail in the next sections. It's also possible to write custom transform steps. Please read the section below to learn more about it.

- resource
- table
- field
- row
- cell

See [Transform Steps](transform-steps.md) for a list of available steps.

## Custom Steps

Here is an example of a custom step written as a python function:

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

def step(resource):
    with resource:
        resource.schema.remove_field("id")
        for row in resource.row_stream:
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

Learn more about custom steps in the [Step Guide](extension/step-guide.md).

## Transform Utils

> Transform Utils is under construction

## Working with PETL

In some cases, it's better to use a lower-level API to achieve some goal. A resource can be exported as a PETL table. For more information please visit PETL's [documentation portal](https://petl.readthedocs.io/en/stable/).

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/transform.csv')
petl_table = resource.to_petl()
# Use it with PETL framework
print(petl_table)
```
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
```
