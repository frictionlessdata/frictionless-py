# Working with Local Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1LiXVkhMg_pD-HI4ANl11tkpZtlba8Q6Z)



> Status: **CORE / STABLE**

You can read and write files locally with Frictionless. It's basic functionality.



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


## Reading Local Data


You can read using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='table.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Local Data

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


## Configuring Local Data

> Not supported