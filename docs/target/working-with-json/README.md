# Working with JSON

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1NLXeYiAxSC0BXZqMRIOSKBo9lk5jkDHf)



> Status: **PLUGIN / STABLE**


```bash
!pip install frictionless
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


You can read CSV using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='table.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing JSON

The same is actual for writing JSON:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.json')
```


```bash
!cat table.new.json
```

## Configuring JSON
