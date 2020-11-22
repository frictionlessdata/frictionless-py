# Working with Inline Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1bsOBn6rDDsZiGS1jCrZ2jskaEBG5wWIq)



> Status: **CORE / STABLE**

Frictionless supports parsing Inline Data.


```bash
!pip install frictionless
```


```bash
! wget -q -O table.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv
! cat table.csv
```

    id,name
    1,english
    2,中国人


## Reading Inline Data


You can read data in this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', 'german')])]


## Writing Inline Data

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(path='table.csv')
resource.write(format='inline')
```




    [['id', 'name'], [1, 'english'], [2, '中国人']]



## Configuring Inline Data

There is a dialect to configure this format, for example:




```python
from frictionless import Resource, dialects

dialect = dialects.InlineDialect(keyed=True)
resource = Resource(data=[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}])
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', 'german')])]


References:
- [I Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#csv)