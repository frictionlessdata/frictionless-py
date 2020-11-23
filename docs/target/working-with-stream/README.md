# Working with Filelike Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1iC0rS6Q80D6lS7Pi6k65bCU5ytNhTtyZ)



> Status: **CORE / STABLE**

Frictionless supports loading Filelike data.


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


## Reading Filelike Data


You can read Filelike using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

with open('table.csv', 'rb') as file:
  resource = Resource(path=file, format='csv')
  print(resource.read_rows())
```

## Writing Filelike Data

The same is actual for writing CSV:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='stream')
```

## Configuring Filelike Data

> Not supported