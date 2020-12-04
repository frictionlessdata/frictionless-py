# Working with Multipart Data

> Status: **STABLE**

You can read and write files split into chunks with Frictionless.

## Reading Multipart Data

You can read using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path=['data/chunk1.csv', 'data/chunk2.csv'])
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Multipart Data

> Not supported

## Configuring Local Data

> Not supported