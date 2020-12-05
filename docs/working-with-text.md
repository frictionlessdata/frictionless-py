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

## Writing Text Data

The same is actual for writing Text Data:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='text', format='csv')
```

## Configuring Text Data

> Not supported
