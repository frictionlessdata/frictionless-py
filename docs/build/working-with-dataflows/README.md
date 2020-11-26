# Working with Dataflows

> Status: **EXPERIMENTAL**

The dataflows pipelines are powered by [DataFlows](http://www.dataflows.org/),
a novel and intuitive way of building data processing flows in Python. Frictionless provides an ability to declaratively describe and run DataFlows pipelines.

```sh
! pip install frictionless[dataflows]
```


```bash
! cat data/capital.csv
```


## Transforming Package

Let's see how we can use a package pipelines to transform data using [DataFlows](http://www.dataflows.org/):

```sh
! cat data/pipeline.yaml
```


```sh
! frictionless transform data/pipeline.yaml
```


Of course, it's possible to do the same using Python programming:

```py
from frictionless import transform

transform(
  {
    "type": "dataflows",
    "steps": [
      {"type": "load", "spec": {"loadSource": "data/capital.csv"}},
      {"type": "set_type", "spec": {"name": "id", "type": "string"}},
      {"type": "dump_to_path", "spec": {"outPath": 'output'}},
    ],
  }
)
```


```sh
! frictionless extract output/datapackage.json
```


DataFlows is a powerful framework. Please read more about it:
- [DataFlows Tutorial](https://github.com/datahq/dataflows/blob/master/TUTORIAL.md)
- [DataFlows Processors](https://github.com/datahq/dataflows/blob/master/PROCESSORS.md)