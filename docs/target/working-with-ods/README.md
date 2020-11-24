# Working with ODS

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1CSZb2Q4JKosx6_X0AdAd8AGiJMP0FiM2)



> Status: **STABLE**

Frictionless supports ODS parsing.


```bash
!pip install frictionless[ods]
```


```bash
! wget -q -O table.ods https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.ods
```

## Reading ODS


You can read this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='table.ods')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing ODS

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.ods')
```




    'table.new.ods'



## Configuring ODS

There is a dialect to configure how Frictionless read and write files in this format. For example:


```python
from frictionless import Resource
from frictionless.plugins.ods import OdsDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.ods', dialect=OdsDialect(sheet='My Table'))
```




    'table.new.ods'



References:
- [ODS Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#ods)