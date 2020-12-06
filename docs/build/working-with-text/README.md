# Working with Text Data

> Status: **STABLE**

Frictionless supports loading textual data

## Reading Text Data

You can read Text Data using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='text://id,name\n1,english\n2,german.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', 'german')])]


## Writing Text Data

The same is actual for writing Text Data:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='text', format='csv')
```




    'id,name\r\n1,english\r\n2,german\r\n'



## Configuring Text Data

There are no options available in `TextControl`.

References:
- [Text Control](https://frictionlessdata.io/tooling/python/controls-reference/#text)