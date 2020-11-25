# Working with CSV

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1AcrdANwgw_wEhqI9ayf4ihJo24LXilFG)



> Status: **STABLE**

CSV is a file format which you can you in Frictionless for reading and writing. Arguable it's the main Open Data format so it's supported very well in Frictionless.


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


## Reading CSV


You can read this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='table.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing CSV

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv')
```




    'table.new.csv'




```bash
!cat table.new.csv
```

    id,name
    1,english
    2,german


## Configuring CSV

There is a dialect to configure how Frictionless read and write files in this format. For example:


```python
from frictionless import Resource
from frictionless.plugins.csv import CsvDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv', dialect=CsvDialect(delimiter=';'))
```




    'table.new.csv'




```bash
!cat table.new.csv
```

    id;name
    1;english
    2;german


References:
- [CSV Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#csv)