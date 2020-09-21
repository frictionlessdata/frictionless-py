# Transforming Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1C4dFWDExyxzGIwLUovrDQZghZK4JK2PD)



> Transform functionality is work-in-progress

Transforming data in Frictionless means modifying a data + metadata set from the state A to the state B. For example, it can be a dirty Excel file we need to transform to a cleaned CSV file or a folder of data files we want to update and save as a data package.

The most high-level way of transforming data is data pipelines. Frictionless supports two types of data pipelines:
- package pipelines
- resource pipelines

The package pipelines are powered by [DataFlows](http://www.dataflows.org/),
a novel and intuitive way of building data processing flows in Python. Frictionless provides an ability to declaratively describe and run DataFlows pipelines.

The resource pipelines are under active development and they are not ready to be used yet. We will update this guide when it's ready adding a resource-level documentation and examples.

Of course, it's not only possible to use pipelines to transform data in Frictionless; we can also use lower-level primitives like `Table` class to modify the data using plain Python programming.




```bash
! pip install frictionless[dataflows]
```


```bash
! wget -q -O capital.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv
! cat capital.csv
```

    id,name
    1,London
    2,Berlin
    3,Paris
    4,Madrid
    5,Rome


## Transform Functions

The high-level interface for validating data provided by Frictionless is a set of `transform` functions:
- `transform`: it will detect the source type and transform data accordingly
- `transform_package`: it transforms a package using a DataFlows pipeline descriptor
- `transform_resource`: it transforms a resource (under construction)

### Transforming Package

Let's see how we can use a package pipelines to transform data using [DataFlows](http://www.dataflows.org/):


```bash
! wget -q -O pipeline.yaml https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/pipeline-docs.yaml
! cat pipeline.yaml
```

    name: pipeline
    type: package
    steps:
      - type: load
        spec:
          loadSource: 'capital.csv'
      - type: set_type
        spec:
          name: id
          type: string
      - type: dump_to_path
        spec:
          outPath: 'output'
          prettyDescriptor: true



```bash
! frictionless transform pipeline.yaml
```

Of course, it's possible to do the same using Python programming:


```python
from frictionless import transform

transform(
  {
    "type": "package",
    "steps": [
      {"type": "load", "spec": {"loadSource": "capital.csv"}},
      {"type": "set_type", "spec": {"name": "id", "type": "string"}},
      {"type": "dump_to_path", "spec": {"outPath": 'output'}},
    ],
  }
)
```


```bash
! ls -la output
```

    total 16
    drwxr-xr-x 2 root root 4096 Aug  4 07:04 .
    drwxr-xr-x 1 root root 4096 Aug  4 07:13 ..
    -rw------- 1 root root   56 Aug  4 07:25 capital.csv
    -rw------- 1 root root  937 Aug  4 07:25 datapackage.json



```bash
! frictionless extract output/datapackage.json
```

    [data] output/capital.csv

      id  name
    ----  ------
       1  London
       2  Berlin
       3  Paris
       4  Madrid
       5  Rome


DataFlows is a powerful framework. Please read more about it:
- [DataFlows Tutorial](https://github.com/datahq/dataflows/blob/master/TUTORIAL.md)
- [DataFlows Processors](https://github.com/datahq/dataflows/blob/master/PROCESSORS.md)

### Transforming Resource

This functionality is under construction.

## Transform Options

For now, the `transorm` function accepts only the `source` option which can be a pipeline descriptor or a resource descriptor (not implemented yet).

**Package**

The `transform_package` functions don't accept any additional arguments.

**Resource**

The `transform_resource` functions don't accept any additional arguments.


## Using Table

On the lowest-level of the transform capabilities we can just use the Table class for whatever manipulations we are interested in. It's just pure Python so you can re-use all your programming skills here. Also, it's important to mention that the approach below is streaming so we can handle very big files. Let's see on an example:


```python
from pprint import pprint
from frictionless import Table

def source():
  with Table('capital.csv') as table:
    for row in table:
      if not row['id'] % 2:
        yield row

with Table(source) as table:
  pprint(table.read_rows())
```

    [Row([('id', 2), ('name', 'Berlin')]), Row([('id', 4), ('name', 'Madrid')])]
