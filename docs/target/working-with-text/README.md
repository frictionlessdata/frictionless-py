# Working with Text Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1mdpneGQU5vMdEZI5AqlOUIfIDd37eZ30)



> Status: **CORE / STABLE**


```bash
!pip install frictionless
```

## Reading Text Data


You can read Text Data using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='text://id,name\n1,english\n2,german', format='csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', 'german')])]


## Writing Text Data

The same is actual for writing Text Data:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.csv')
```


```bash
!cat table.new.csv
```

## Configuring Text Data
