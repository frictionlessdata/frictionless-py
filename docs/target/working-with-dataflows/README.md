# Working with Dataflows

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1MbEhvyrIIW6lExySC48pakjLSAqxHj3t)



> Status: **PLUGIN / EXPERIMENTAL**

The dataflows pipelines are powered by [DataFlows](http://www.dataflows.org/),
a novel and intuitive way of building data processing flows in Python. Frictionless provides an ability to declaratively describe and run DataFlows pipelines.


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


## Transforming Package

Let's see how we can use a package pipelines to transform data using [DataFlows](http://www.dataflows.org/):


```bash
! wget -q -O pipeline.yaml https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/pipeline-docs.yaml
! cat pipeline.yaml
```

    name: pipeline
    type: dataflows
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
    "type": "dataflows",
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
    drwxr-xr-x 2 root root 4096 Nov  3 11:36 .
    drwxr-xr-x 1 root root 4096 Nov  3 11:36 ..
    -rw------- 1 root root   56 Nov  3 11:36 capital.csv
    -rw------- 1 root root  937 Nov  3 11:36 datapackage.json



```bash
! frictionless extract output/datapackage.json
```

    [data] output/capital.csv

    ==  ======
    id  name
    ==  ======
    1   London
    2   Berlin
    3   Paris
    4   Madrid
    5   Rome
    ==  ======



DataFlows is a powerful framework. Please read more about it:
- [DataFlows Tutorial](https://github.com/datahq/dataflows/blob/master/TUTORIAL.md)
- [DataFlows Processors](https://github.com/datahq/dataflows/blob/master/PROCESSORS.md)