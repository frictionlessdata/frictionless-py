# Remote Scheme

You can read files remotely with Frictionless. This is a basic functionality of Frictionless.

## Reading Data

You can read using `Package/Resource`, for example:

```python tabs=Python
from pprint import pprint
from frictionless import Resource

path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv'
resource = Resource(path=path)
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

A similar approach can be used for writing:

```python tabs=Python
from frictionless import Resource

resource = Resource(path='data/table.csv')
resource.write('https://example.com/data/table.csv') # will POST the file to the server
```

## Configuration

There is a `Control` to configure remote data, for example:

```python tabs=Python
from frictionless import Resource
from frictionless.plugins.remote import RemoteControl

control = RemoteControl(http_timeout=10)
path='https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv'
resource = Resource(path=path, control=control)
print(resource.to_view())
```
```
+----+-----------+
| id | name      |
+====+===========+
|  1 | 'english' |
+----+-----------+
|  2 | '中国人'     |
+----+-----------+
```

## Reference

```yaml reference
references:
  - frictionless.schemes.RemoteControl
```
