# Working with Inline Data

> Status: **STABLE**

Frictionless supports parsing Inline Data.

```bash
! cat data/table.csv
```

## Reading Inline Data

You can read data in this format using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
print(resource.read_rows())
```

## Writing Inline Data

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write(format='inline')
```

## Configuring Inline Data

There is a dialect to configure this format, for example:

```python
from frictionless import Resource
from frictionless.plugins.inline import InlineDialect

dialect = InlineDialect(keyed=True, keys=['name', 'id'])
resource = Resource(data=[{'id': 1, 'name': 'english'}, {'id': 2, 'name': 'german'}], dialect=dialect)
print(resource.read_rows())
```

References:
- [Inline Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#inline)
