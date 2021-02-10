---
title: Resource Guide
---

> This guide in under development. We are moving some shared Resource information from describe, extract, validate, and transform guides to this guide.

## Infer Options

Let's explore some handy options to customize the infer process. All of them are available in some form for all the functions above and for different invocation types: in Python, in CLI, or for a REST server.

### Infer Type

This option allows manually setting all the field types to a given type. It's useful when you need to skip data casting (setting `any` type) or have everything as a string (setting `string` type):


```python
! frictionless describe data/country-1.csv --infer-type string
```

    ---
    metadata: data/country-1.csv
    ---

    compression: 'no'
    compressionPath: ''
    control:
      newline: ''
    dialect: {}
    encoding: utf-8
    format: csv
    hashing: md5
    name: country-1
    path: data/country-1.csv
    profile: tabular-data-resource
    query: {}
    schema:
      fields:
        - name: id
          type: string
        - name: neighbor_id
          type: string
        - name: name
          type: string
        - name: population
          type: string
    scheme: file
    stats:
      bytes: 100
      fields: 4
      hash: 4204f087f328b70c854c03403ab448c4
      rows: 5



### Infer Names

Sometimes you don't want to use existent header row to compose field names. It's possible to provide custom names:


```python
from frictionless import describe

resource = describe("data/country-1.csv", infer_names=["f1", "f2", "f3", "f4"])
print(resource.schema.field_names)
```

    ['f1', 'f2', 'f3', 'f4']


### Infer Volume

By default, Frictionless will use the first 100 rows to detect field types. This can be customized. The following code will be slower but the result can be more accurate


```python
from frictionless import describe

resource = describe("data/country-1.csv", infer_volume=1000)
```

### Infer Confidence

By default, Frictionless uses 0.9 (90%) confidence level for data types detection. It means that it there are 9 integers in a field and one string it will be inferred as an integer. If you want a guarantee that an inferred schema will conform to the data you can set it to 1 (100%):


```python
from frictionless import describe

resource = describe("data/country-1.csv", infer_confidence=1)
```

### Infer Missing Values

Missing Values is an important concept in data description. It provides information about what cell values should be considered as nulls. We can customize the defaults:


```python
from pprint import pprint
from frictionless import describe

resource = describe("data/country-1.csv", infer_missing_values=["", "67"])
pprint(resource.schema.missing_values)
pprint(resource.read_rows())
```

    ['', '67']
    [Row([('id', 1),
          ('neighbor_id', None),
          ('name', 'Britain'),
          ('population', None)]),
     Row([('id', 2), ('neighbor_id', 3), ('name', 'France'), ('population', None)]),
     Row([('id', 3), ('neighbor_id', 2), ('name', 'Germany'), ('population', 83)]),
     Row([('id', 4), ('neighbor_id', 5), ('name', 'Italy'), ('population', 60)]),
     Row([('id', 5), ('neighbor_id', 4), ('name', 'Spain'), ('population', 47)])]


As we can see, the textual values equal to "67" are now considered nulls. Usually, it's handy when you have data with values like: '-', 'n/a', and similar.
