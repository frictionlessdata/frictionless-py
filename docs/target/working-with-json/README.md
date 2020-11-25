# Working with JSON

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1NLXeYiAxSC0BXZqMRIOSKBo9lk5jkDHf)



> Status: **STABLE**

Frictionless supports parsing JSON tables (json and jsonl/ndjson).


```bash
!pip install frictionless[json]
```


```bash
! wget -q -O table.json https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.json
! cat table.json
```

    [
        ["id", "name"],
        [1, "english"],
        [2, "中国人"]
    ]


## Reading JSON


You can read this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='table.json')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing JSON

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.json')
```




    'table.new.json'




```bash
!cat table.new.json
```

    [
      [
        "id",
        "name"
      ],
      [
        1,
        "english"
      ],
      [
        2,
        "german"
      ]
    ]

## Configuring JSON

There is a dialect to configure how Frictionless read and write files in this format. For example:


```python
from frictionless import Resource
from frictionless.plugins.json import JsonDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.json', dialect=JsonDialect(keyed=True))
```




    'table.new.json'




```bash
!cat table.new.json
```

    [
      {
        "id": 1,
        "name": "english"
      },
      {
        "id": 2,
        "name": "german"
      }
    ]

References:
- [JSON Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#csv)