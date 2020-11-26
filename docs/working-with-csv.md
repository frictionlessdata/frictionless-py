# Working with CSV

> Status: **STABLE**

CSV is a file format which you can you in Frictionless for reading and writing. Arguable it's the main Open Data format so it's supported very well in Frictionless.

```python
! cat data/table.csv
```

## Reading CSV

You can read this format using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(path='data/table.csv')
print(resource.read_rows())
```

## Writing CSV

The same is actual for writing:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv')
```

```python
!cat tmp/table.csv
```

## Configuring CSV

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python
from frictionless import Resource
from frictionless.plugins.csv import CsvDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.csv', dialect=CsvDialect(delimiter=';'))
```

```python
!cat tmp/table.csv
```

References:
- [CSV Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#csv)
