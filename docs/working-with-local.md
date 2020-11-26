# Working with Local Data

> Status: **STABLE**

You can read and write files locally with Frictionless. It's basic functionality.

## Reading Local Data

You can read using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(path='data/table.csv')
print(resource.read_rows())
```

## Writing Local Data

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv')
```

```bash
!cat tmp/table.csv
```

## Configuring Local Data

> Not supported
