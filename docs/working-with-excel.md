# Working with Excel

> Status: **STABLE**

Excel is a very popular tabular data format that usually has `xlsx` (newer) and `xls` (older) file extensions. Frictionless supports Excel files extensively.

```sh
!pip install frictionless[excel]
```

## Reading Excel

You can read this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='data/table.xlsx')
print(resource.read_rows())
```

## Writing Excel

The same is actual for writing:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.xlsx')
```

## Configuring Excel

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python
from frictionless import Resource
from frictionless.plugins.excel import ExcelDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.xlsx', dialect=ExcelDialect(sheet='My Table'))
```

References:
- [Excel Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#excel)
