# Working with ODS

> Status: **STABLE**

Frictionless supports ODS parsing.

```sh
!pip install frictionless[ods]
```

## Reading ODS

You can read this format using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(path='data/table.ods')
print(resource.read_rows())
```

## Writing ODS

The same is actual for writing:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.ods')
```

## Configuring ODS

There is a dialect to configure how Frictionless read and write files in this format. For example:


```python
from frictionless import Resource
from frictionless.plugins.ods import OdsDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.ods', dialect=OdsDialect(sheet='My Table'))
```

References:
- [ODS Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#ods)
