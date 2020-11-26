# Working with JSON

> Status: **STABLE**

Frictionless supports parsing JSON tables (json and jsonl/ndjson).

```sh
!pip install frictionless[json]
```


```bash
! cat data/table.json
```


## Reading JSON

You can read this format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='data/table.json')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing JSON

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.json')
```




    'tmp/table.json'



```bash
!cat tmp/table.json
```


## Configuring JSON

There is a dialect to configure how Frictionless read and write files in this format. For example:


```python
from frictionless import Resource
from frictionless.plugins.json import JsonDialect

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.json', dialect=JsonDialect(keyed=True))
```




    'tmp/table.json'



```bash
!cat tmp/table.json
```


References:
- [JSON Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#csv)