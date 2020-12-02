# Working with HTML

> Status: **EXPERIMENTAL**

Frictionless supports parsing HTML format

```sh
!pip install frictionless[html]
```

```python
! cat data/table1.html
```

## Reading HTML

You can this file format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='data/table1.html')
print(resource.read_rows())
```

## Writing HTML

The same is actual for writing:

```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.html')
```

```python
!cat tmp/table.html
```

## Configuring HTML

There is a dialect to configure HTML, for example:

```py
from frictionless import Resource
from frictionless.plugins.html import HtmlDialect

resource = Resource(path='data/table1.html', dialect=HtmlDialect(selector='#id'))
print(resource.read_rows())
```

References:
- [HTML Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#html)
