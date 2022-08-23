---
script:
  basepath: data
---

# Transforming Data

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Transforming data in Frictionless means modifying data and metadata from state A to state B. For example, it could be transforming a messy Excel file to a cleaned CSV file, or transforming a folder of data files to a data package we can publish more easily. To read more about the concepts behind Frictionless Transform, please check out the [Transform Principles](#transform-principles) sections belows.

In comparison to similiar Python software like Pandas, Frictionless provides better control over metadata, has a modular API, and fully supports Frictionless Specifications. Also, it is a streaming framework with an ability to work with large data. As a downside of the Frictionless architecture, it might be slower compared to other Python packages, especially to projects like Pandas.

Keep reading below to learn about the principles underlying Frictionless Transform, or [skip ahead](/docs/guides/transform-guide#transform-functions) to see how to use the Transform code.

## Transform Principles

Frictionless Transform is based on a few core principles which are shared with other parts of the framework:

### Conceptual Simplicity

Frictionless Transform can be thought of as a list of functions that accept a source resource/package object and return a target resource/package object. Every function updates the input's metadata and data - and nothing more. We tried to make this straightforward and conceptually simple, because we want our users to be able to understand the tools and master them.

### Metadata Matters

There are plenty of great ETL-frameworks written in Python and other languages. We use one of them (PETL) under the hood (described in more detail later). The core difference between Frictionless and others is that we treat metadata as a first-class citizen. This means that you don't lose type and other important information during the pipeline evaluation.

### Data Streaming

Whenever possible, Frictionless streams the data instead of reading it into memory. For example, for sorting big tables we use a memory usage threshold and when it is met we use the file system to unload the data. The ability to stream data gives users power to work with files of any size, even very large files.

### Lazy Evaluation

With Frictionless all data manipulation happens on-demand. For example, if you reshape one table in a data package containing 10 big csv files, Frictionless will not even read the 9 other tables. Frictionless tries to be as explicit as possible regarding actions taken. For example, it will not use CPU resources to cast data unless a user adds a `normalize` step. So it's possible to transform a rather big file without even casting types, for example, if you only need to reshape it.

### Software Reuse

For the core transform functions, Frictionless uses the amazing [PETL](https://petl.readthedocs.io/en/stable/) project under the hood. This library provides lazy-loading functionality in running data pipelines. On top of PETL, Frictionless adds metadata management and a bridge between Frictionless concepts like Package/Resource and PETL's processors.

## Transform Functions

Frictionless supports a few different kinds of data and metadata transformations:
- resource and package transformations
- transformations based on a declarative pipeline

The main difference between these is that resource and package transforms are imperative while pipelines can be created beforehand or shared as a JSON file. We'll talk more about pipelines in the [Transforming Pipeline](#transforming-pipeline) section below. First, we will introduce the transform functions, then go into detail about how to transform a resource and a package. As a reminder, in the Frictionless ecosystem, a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema. This concept is described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction).

> Download [`transform.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/transform.csv) to reproduce the examples (right-click and "Save link as". You might need to change the file extension from .txt to .csv).

```bash script tabs=CLI
cat transform.csv
```

The high-level interface to transform data is a set of `transform` functions:
- `transform`: detects the source type and transforms data accordingly
- `reosurce.transform`: transforms a resource
- `package.transform`: transforms a package

We'll see examples of these functions in the next few sections.

## Transforming a Resource

Let's write our first transformation. Here, we will transform a data file (a resource) by defining a source resource, applying transform steps and getting back a resulting target resource:

```python script tabs=Python
from frictionless import Resource, Pipeline, steps

# Define source resource
source = Resource(path="transform.csv")

# Create a pipeline
pipeline = Pipeline(steps=[
    steps.table_normalize(),
    steps.field_add(name="cars", formula='population*2', descriptor={'type': 'integer'}),
])

# Apply transform pipeline
target = source.transform(pipeline)

# Print resulting schema and data
print(target.schema)
print(target.to_view())
```

Let's break down the transforming steps we applied:
1. `steps.table_normalize` - cast data types and shape the table according to the schema, inferred or provided
1. `steps.field_add` - adds a field to data and metadata based on the information provided by the user

There are many more available steps that we will cover below.

## Transforming a Package

A package is a set of resources. Transforming a package means adding or removing resources and/or transforming those resources themselves. This example shows how transforming a package is similar to transforming a single resource:

```python script tabs=Python
from frictionless import Package, Resource, transform, steps

# Define source package
source = Package(resources=[Resource(name='main', path="transform.csv")])

# Create a pipeline
pipeline = Pipeline(steps=[
    steps.resource_add(name="extra", descriptor={"data": [['id', 'cars'], [1, 166], [2, 132], [3, 94]]}),
    steps.resource_transform(
        name="main",
        steps=[
            steps.table_normalize(),
            steps.table_join(resource="extra", field_name="id"),
        ],
    ),
    steps.resource_remove(name="extra"),
])

# Apply transform steps
target = source.transform(pipeline)

# Print resulting resources, schema and data
print(target.resource_names)
print(target.get_resource("main").schema)
print(target.get_resource("main").to_view())
```

We have basically done the same as in [Transforming a Resource](#transforming-a-resource) section. This example is quite artificial and created only to show how to join two resources, but hopefully it provides a basic understanding of how flexible package transformations can be.

## Transforming Pipeline

A pipeline is a declarative way to write out metadata transform steps. With a pipeline, you can transform a resource, package, or write custom plugins too.

For resource and package types it's mostly the same functionality as we have seen above, but written declaratively. So let's run the same resource transformation as we did in the [Transforming a Resource](#transforming-a-resource) section:

```python script tabs=Python
from frictionless import Pipeline, transform

pipeline = Pipeline.from_descriptor({
    "steps": [
        {"type": "table-normalize"},
        {
            "type": "field-add",
            "name": "cars",
            "formula": "population*2",
            "descriptor": {"type": "integer"}
        },
    ],
})
print(pipeline)
```

So what's the reason to use declarative pipelines if it works the same as the Python code? The main difference is that pipelines can be saved as JSON files which can be shared among different users and used with CLI and API. For example, if you implement your own UI based on Frictionless Framework you can serialize the whole pipeline as a JSON file and send it to the server. This is the same for CLI - if your colleague has  given you a `pipeline.json` file, you can run `frictionless transform pipeline.json` in the CLI to get the same results as they got.

## Available Steps

Frictionless includes more than 40+ built-in transform steps. They are grouped by the object so you can find them easily using code auto completion in a code editor. For example, start typing `steps.table...` and you will see all the available steps for that group. The available groups are:

- resource
- table
- field
- row
- cell

See [Transform Steps](../steps/cell.md) for a list of all available steps. It is also possible to write custom transform steps: see the next section.

## Custom Steps

Here is an example of a custom step written as a Python function. This example step removes a field from a data table (note: Frictionless already has a built-in function that does this same thing: `steps.field_remove`).

```python script tabs=Python
from frictionless import Package, Resource, Step, transform, steps

class custom_step(Step):
    def transform_resource(self, resource):
        current = resource.to_copy()

        # Data
        def data():
            with current:
                for list in current.cell_stream:
                    yield list[1:]

        # Meta
        resource.data = data
        resource.schema.remove_field("id")

source = Resource("transform.csv")
pipeline = Pipeline(steps=[custom_step()])
target = source.transform(pipeline)
print(target.schema)
print(target.to_view())
```

As you can see you can implement any custom steps within a Python script. To make it work within a declarative pipeline you need to implement a plugin. Learn more about [Custom Steps](extension/step-guide.md) and [Plugins](extension/plugin-guide.md).

## Transform Utils

> Transform Utils is under construction.

## Working with PETL

In some cases, it's better to use a lower-level API to achieve your goal. A resource can be exported as a PETL table. For more information please visit PETL's [documentation portal](https://petl.readthedocs.io/en/stable/).

```python script tabs=Python
from frictionless import Resource

resource = Resource(path='transform.csv')
petl_table = resource.to_petl()
# Use it with PETL framework
print(petl_table)
```
