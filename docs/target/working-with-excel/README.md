# Working with Excel

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1iO18YVjn9xCB0SpPu6Fgt0SLvkS8d41U)



> Status: **STABLE**

Excel is a very popular tabular data format that usually has `xlsx` (newer) and `xls` (older) file extensions. Frictionless supports Excel files extensively.


```bash
!pip install frictionless[excel]
```


```bash
! wget -q -O table.xlsx https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.xlsx
```

## Reading Excel

You can read this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='table.xlsx')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Excel

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.xlsx')
```




    'table.new.xlsx'



## Configuring Excel

There is a dialect to configure how Frictionless read and write files in this format. For example:


```python
from frictionless import Resource
from frictionless.plugins.excel import ExcelDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('table.new.xlsx', dialect=ExcelDialect(sheet='My Table'))
```




    'table.new.xlsx'



References:
- [Excel Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#excel)