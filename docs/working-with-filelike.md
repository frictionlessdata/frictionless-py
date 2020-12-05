# Working with Filelike Data

> Status: **STABLE**

Frictionless supports loading Filelike data.

## Reading Filelike Data

You can read Filelike using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

with open('data/table.csv', 'rb') as file:
  resource = Resource(path=file, format='csv')
  print(resource.read_rows())
```

## Writing Filelike Data

The same is actual for writing CSV:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write(scheme='filelike', format='csv')
```

## Configuring Filelike Data

> Not supported
