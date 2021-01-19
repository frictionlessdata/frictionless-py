---
title: HTML Tutorial
---

:::caution Plugin
Status: **EXPERIMENTAL**
:::

Frictionless supports parsing HTML format

```bash
!pip install frictionless[html]
```



```python
! cat data/table1.html
```

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body>
        <table>
            <tr>
                <td>id</td>
                <td>name</td>
            </tr>
            <tr>
                <td>1</td>
                <td>english</td>
            </tr>
            <tr>
                <td>2</td>
                <td>中国人</td>
            </tr>
        </table>
    </body>
    </html

## Reading HTML

You can this file format using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='data/table1.html')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing HTML

The same is actual for writing:


```python
from frictionless import Resource

resource = Resource(data=[['id', 'name'], [1, 'english'], [2, 'german']])
resource.write('tmp/table.html')
```




    'tmp/table.html'




```python
!cat tmp/table.html
```

    <html><body><table>
    <tr><td>id</td><td>name</td></tr>
    <tr><td>1</td><td>english</td></tr>
    <tr><td>2</td><td>german</td></tr>
    </table></body></html>

## Configuring HTML

There is a dialect to configure HTML, for example:

```python
from frictionless import Resource
from frictionless.plugins.html import HtmlDialect

resource = Resource(path='data/table1.html', dialect=HtmlDialect(selector='#id'))
print(resource.read_rows())
```


References:
- [HTML Dialect](https://frictionlessdata.io/tooling/python/formats-reference/#html)
