# Working with Remote Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/19NgoHIXWHJNKFQl50YV7C396xRtrqf3o)



> Status: **STABLE**

You can read files remotely with Frictionless. It's basic functionality.



```bash
!pip install frictionless
```

## Reading Remote Data


You can read using `Package/Resource` or `Table` API, for example:


```python
from frictionless import Resource

resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv')
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]


## Writing Remote Data

> Not supported

## Configuring Remote Data

There is a control to configure remote data, for example:


```python
from frictionless import Resource, controls

control = controls.RemoteControl(http_timeout=10)
resource = Resource(path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv', control=control)
print(resource.read_rows())
```

    [Row([('id', 1), ('name', 'english')]), Row([('id', 2), ('name', '中国人')])]




References:
- [Remote Control](https://frictionlessdata.io/tooling/python/schemes-reference/#remote)