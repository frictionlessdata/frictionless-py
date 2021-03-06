---
title: Transform Guide
---

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Transforming data in Frictionless means modifying data and metadata from state A to state B. For example, it could be transforming a messy Excel file to a cleaned CSV file. Or updating a folder of data files to a data package we can publish.

For the core transform functions, Frictionless uses the amazing [PETL](https://petl.readthedocs.io/en/stable/) project under the hood. This library provides lazy-loading functionality in running data pipelines. On top of it Frictionless adds metadata management and a bridge between already familiar concepts like Package/Resource and PETL's processors.

Frictionless supports a few different kinds of data and metadata transformations:
- resource and package transformations
- transformations based on a declarative pipeline

The main difference between these is that resource and package transforms are imperative while pipelines can be created beforehand or shared as a JSON file.

> Download [`transform.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/transform.csv) into the `data` folder to reproduce the examples.

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

The high-level interface to transform data is a set of `transform` functions:
- `transform`: detects the source type and transforms data accordingly
- `transform_resource`: transforms a resource
- `transform_package`: transforms a package
- `transform_pipeline`: transforms a resource or package based on a declarative pipeline definition

## Transforming Resource

Let's write our first transform. It's as straightforward as defining a source resource, applying transform steps and getting back a resulting target resource:

```python title="Python"
from pprint import pprint
from frictionless import Resource, transform, steps

# Define source resource
source = Resource(path="data/transform.csv")

# Apply transform steps
target = transform(
    source,
    steps=[
        steps.table_normalize(),
        steps.table_melt(field_name="name"),
    ],
)

# Print resulting schema and data
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

Let's break down the transforming steps we applied:
1. `steps.table_normalize` - cast data types and shape the table according to the schema, inferred or provided
2. `steps.table_melt` - melt the table as it is done in R-Language or in other scientific libraries like `pandas`

There are dozens of other available steps that will be covered below.

## Transforming Package

A package is a set of resources. Transforming a package means adding or removing resources and/or transforming those resources themselves:

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

# Define source package
source = Package(resources=[Resource(name='main', path="data/transform.csv")])

# Apply transform steps
target = transform(
    source,
    steps=[
        steps.resource_add(name="extra", path="data/transform.csv"),
        steps.resource_transform(
            name="main",
            steps=[
                steps.table_merge(resource="extra"),
                steps.row_sort(field_names=["id"]),
            ],
        ),
        steps.resource_remove(name="extra"),
    ],
)

# Print resulting resources, schema and data
pprint(target.resource_names)
pprint(target.get_resource("main").schema)
pprint(target.get_resource("main").read_rows())
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

The exact transformation we have applied actually doesn't make much sense as we just duplicated every row of the `main` resource. But hopefully this example provids a basic understanding of how simple, and at the same time flexible, package transformations can be.

## Transforming Pipeline

A pipeline is a metadata object having one of these types:
- resource
- package
- others (depending on custom plugins you use)

For resource and package types it's basically the same functionality as we have seen above, but written declaratively. So let's run the same resource transformation as we did in the `Transforming Resource` section:

```python title="Python"
from pprint import pprint
from frictionless import Pipeline, transform

pipeline = Pipeline(
    {
        "tasks": [
            {
                "type": "resource",
                "source": {"path": "data/transform.csv"},
                "steps": [
                    {"code": "table-normalize"},
                    {"code": "table-melt", "fieldName": "name"},
                ],
            }
        ]
    }
)
status = transform(pipeline)
pprint(status.task.target.schema)
pprint(status.task.target.read_rows())
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

It returns the same result as in `Transform resource`.

## Transform Principles

Frictionless Transform is based on a few core principles which are shared with other parts of the framework:

### Conceptual Simplicity

Frictionless Transform is not more than a list of functions that accepts a source resource/package object and returns a target resource/package object. Every function updates the input's metadata and data - and that's it. Thanks to this simplicity even a non-technical user can read the [source code](https://github.com/frictionlessdata/frictionless-py/blob/7ad8e692ad00131cdc9fa51258d8b860c62e77bc/frictionless/transform/resource.py#L7) of the transform function and understand how it works. We tried to make this simple, because understanding the tools you use can be really important for mastering them.

### Metadata Matters

There are plenty of great ETL-frameworks written in Python and other languages. As we mentioned earlier, we use one of them (PETL) under the hood. The core difference between Frictionless and others is that we treat metadata as a first-class citizen. This means that you don't lose type and other important information during the pipeline evaluation.

### Data Streaming

Whenever possible, Frictionless streams the data instead of reading it into memory. For example, for sorting big tables we use a memory usage threshold and when it is met we use the file system to unload the data. The ability to stream data gives users power to work with files of any size.

### Lazy Evaluation

Unlike some systems like `Data Package Pipelines`, the core Frictionless Transform doesn't have a back-pressured flow, since all data manipulation happens on-demand. For example, if you reshape one table in a data package containing 10 big csv files, Frictionless will not even read the 9 other tables. Actually, when you call `target = transform(source)` it does almost nothing until a data reading call like `target.read_rows()` is made.

### Lean Processing

Similar to the section above, Frictionless tries to be as explicit as possible regarding actions taken. For example, it will not use CPU resources to cast data unless a user adds a `normalize` step, `validate` step, or similar steps. So it's possible to transform a rather big file without even casting types, for example, if you only need to reshape it.

## Available Steps

Frictionless includes more than 40+ built-in transform steps. They are grouped by the object so you can find them easily using code auto completion. For example, start typing `steps.table...` and you will see all the available steps for that group. The available groups are:

- resource
- table
- field
- row
- cell

See [Transform Steps](transform-steps.md) for a list of all available steps. It is also possible to write custom transform steps: see the next section.

## Custom Steps

Here is an example of a custom step written as a Python function:

```python title="Python"
from pprint import pprint
from frictionless import Package, Resource, transform, steps

def step(resource):
    current = resource.to_copy()

    # Data
    def data():
        with current:
            for list in current.list_stream:
                yield list[1:]

    # Meta
    resource.data = data
    resource.schema.remove_field("id")


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

> Transform Utils is under construction.

## Working with PETL

In some cases, it's better to use a lower-level API to achieve your goal. A resource can be exported as a PETL table. For more information please visit PETL's [documentation portal](https://petl.readthedocs.io/en/stable/).

```python title="Python"
from frictionless import Resource

resource = Resource(path='data/transform.csv')
petl_table = resource.to_petl()
# Use it with PETL framework
print(petl_table)
```
```
+----+---------+------------+
| id | name    | population |
+====+=========+============+
| 1  | germany | 83         |
+----+---------+------------+
| 2  | france  | 66         |
+----+---------+------------+
| 3  | spain   | 47         |
+----+---------+------------+
```
