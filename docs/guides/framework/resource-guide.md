---
title: Resource Guide
goodread:
  cleanup:
    - rm resource.json
    - rm resource.yaml
---

The Resource class is arguable the most important class of the whole Frictionless Framework. It's based on [Data Resource Spec](https://specs.frictionlessdata.io/data-resource/) and  [Tabular Data Resource Spec](https://specs.frictionlessdata.io/data-resource/)

## Creating Resource

Let's create a data resource:

```python goodread title="Python"
from frictionless import Resource

resource = Resource('data/table.csv') # from a resource path
resource = Resource('data/resource.json') # from a descriptor path
resource = Resource({'path': 'data/table.csv'}) # from a descriptor
resource = Resource(path='data/table.csv') # from arguments
```

As you can see it's possible to create a resource providing different kinds of sources which will be detector to have some type automatically (e.g. whether it's a descriptor or a path). It's possible to make this step more explicit:

```python goodread title="Python"
from frictionless import Resource

resource = Resource(path='data/table.csv') # from a path
resource = Resource(descriptor='data/resource.json') # from a descriptor
```

## Describing Resource

The specs support a great deal of resource metadata which is possible to have with Frictionless Framework too:

```python goodread title="Python"
from frictionless import Resource

resource = Resource(
    name='resource',
    title='My Resource',
    description='My Resource for the Guide',
    path='data/table.csv',
    # it's possible to provide all the official properties like mediatype, etc
)
```

If you have created a resource, for example, from a descriptor you can access this properties:

```python goodread title="Python"
from frictionless import Resource

resource = Resource('data/resource.json')
resource.name
resource.title
resource.description
# and others
```

And edit them:

```python goodread title="Python"
from frictionless import Resource

resource = Resource('data/resource.json')
resource.name = 'new-name'
resource.title = 'New Title'
resource.description = 'New Description'
# and others
```

## Saving Descriptor

As any of the Metadata classes the Resource class can be saved as JSON or YAML:

```python goodread title="Python"
from frictionless import Resource
resource = Resource('data/table.csv')
resource.to_json('resource.json') # Save as JSON
resource.to_yaml('resource.yaml') # Save as YAML
```

## Resource Lifecycle

You might have noticed that we had to duplicate the `with Resource(...)` statement in some examples. The reason is that Resource is a streaming interface. Once it's read you need to open it again. Let's show it in an example:

```python goodread title="Python"
from pprint import pprint
from frictionless import Resource

resource = Resource('data/capital-3.csv')
resource.open()
pprint(resource.read_rows())
pprint(resource.read_rows())
# We need to re-open: there is no data left
resource.open()
pprint(resource.read_rows())
# We need to close manually: not context manager is used
resource.close()
```
```
[{'id': 1, 'name': 'London'},
 {'id': 2, 'name': 'Berlin'},
 {'id': 3, 'name': 'Paris'},
 {'id': 4, 'name': 'Madrid'},
 {'id': 5, 'name': 'Rome'}]
[]
[{'id': 1, 'name': 'London'},
 {'id': 2, 'name': 'Berlin'},
 {'id': 3, 'name': 'Paris'},
 {'id': 4, 'name': 'Madrid'},
 {'id': 5, 'name': 'Rome'}]
```

At the same you can read data for a resource without opening and closing it explicitly. In this case Frictionless Framework will open and close the resource for you so it will be basically a one-time operation:

```python goodread title="Python"
from frictionless import Resource

resource = Resource('data/capital-3.csv')
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'London'},
 {'id': 2, 'name': 'Berlin'},
 {'id': 3, 'name': 'Paris'},
 {'id': 4, 'name': 'Madrid'},
 {'id': 5, 'name': 'Rome'}]
```

## Reading Data

The Resource class is also a metadata class which provides various read and stream functions. The `extract` functions always read rows into memory; Resource can do the same but it also gives a choice regarding output data. It can be `rows`, `data`, `text`, or `bytes`. Let's try reading all of them:

```python goodread title="Python"
from frictionless import Resource

resource = Resource('data/country-3.csv')
pprint(resource.read_bytes())
pprint(resource.read_text())
pprint(resource.read_lists())
pprint(resource.read_rows())
```
```
(b'id,capital_id,name,population\n1,1,Britain,67\n2,3,France,67\n3,2,Germany,8'
 b'3\n4,5,Italy,60\n5,4,Spain,47\n')
('id,capital_id,name,population\n'
 '1,1,Britain,67\n'
 '2,3,France,67\n'
 '3,2,Germany,83\n'
 '4,5,Italy,60\n'
 '5,4,Spain,47\n')
[['id', 'capital_id', 'name', 'population'],
 ['1', '1', 'Britain', '67'],
 ['2', '3', 'France', '67'],
 ['3', '2', 'Germany', '83'],
 ['4', '5', 'Italy', '60'],
 ['5', '4', 'Spain', '47']]
[{'id': 1, 'capital_id': 1, 'name': 'Britain', 'population': 67},
 {'id': 2, 'capital_id': 3, 'name': 'France', 'population': 67},
 {'id': 3, 'capital_id': 2, 'name': 'Germany', 'population': 83},
 {'id': 4, 'capital_id': 5, 'name': 'Italy', 'population': 60},
 {'id': 5, 'capital_id': 4, 'name': 'Spain', 'population': 47}]
```

It's really handy to read all your data into memory but it's not always possible if a file is really big. For such cases, Frictionless provides streaming functions:

```python goodread title="Python"
from frictionless import Resource

with Resource('data/country-3.csv') as resource:
    pprint(resource.byte_stream)
    pprint(resource.text_stream)
    pprint(resource.list_stream)
    pprint(resource.row_stream)
    for row in resource.row_stream:
      print(row)
```
```
<frictionless.loader.ByteStreamWithStatsHandling object at 0x7ff1d141b2e0>
<_io.TextIOWrapper name='data/country-3.csv' encoding='utf-8'>
<itertools.chain object at 0x7ff1d1427040>
<generator object Resource.__read_row_stream.<locals>.row_stream at 0x7ff1d1483510>
{'id': 1, 'capital_id': 1, 'name': 'Britain', 'population': 67}
{'id': 2, 'capital_id': 3, 'name': 'France', 'population': 67}
{'id': 3, 'capital_id': 2, 'name': 'Germany', 'population': 83}
{'id': 4, 'capital_id': 5, 'name': 'Italy', 'population': 60}
{'id': 5, 'capital_id': 4, 'name': 'Spain', 'population': 47}
```

## File Details

Let's overview the details we can specify for a file. Usually you don't need to provide those details as Frictionless is capable to infer it on its own. Although, there are situation when you need to specify it manually. The following example will use the `Resource` class but the same options can be used for the `extract` and `extract_table` functions.

### Scheme

The scheme also know as protocol indicates which loader Frictionless should use to read or write data. It can be `file` (default), `text`, `http`, `https`, `s3`, and others.

```python goodread title="Python"
from frictionless import Resource

with Resource(b'header1,header2\nvalue1,value2', format='csv') as resource:
  print(resource.scheme)
  print(resource.read_rows())
```
```
buffer
[{'header1': 'value1', 'header2': 'value2'}]
```

### Format

The format or as it's also called extension helps Frictionless to choose a proper parser to handle the file. Popular formats are `csv`, `xlsx`, `json` and others

```python goodread title="Python"
from frictionless import Resource

with Resource(b'header1,header2\nvalue1,value2.csv', format='csv') as resource:
  print(resource.format)
  print(resource.read_rows())
```
```
csv
[{'header1': 'value1', 'header2': 'value2.csv'}]
```

### Hashing

The hashing option controls which hashing algorithm should be used for generating the `hash` property. It doesn't affect the `extract` function but can be used with the `Resource` class:

```python goodread title="Python"
from frictionless import Resource

with Resource('data/country-3.csv', hashing='sha256') as resource:
  resource.read_rows()
  print(resource.hashing)
  print(resource.stats['hash'])
```
```
sha256
408b5058f961915c1e1f3bc318ab01d7d094a4daccdf03ad6022cfc7b8ea4e3e
```

### Encoding

Frictionless automatically detects encoding of files but sometimes it can be inaccurate. It's possible to provide an encoding manually:

```python goodread title="Python"
from frictionless import Resource

with Resource('data/country-3.csv', encoding='utf-8') as resource:
  print(resource.encoding)
  print(resource.path)
```
```
utf-8
data/country-3.csv
```

### Innerpath

By default, Frictionless uses the first file found in a zip archive. It's possible to adjust this behaviour:

```python goodread title="Python"
from frictionless import Resource

with Resource('data/table-multiple-files.zip', innerpath='table-reverse.csv') as resource:
  print(resource.compression)
  print(resource.innerpath)
  print(resource.read_rows())
```
```
zip
table-reverse.csv
[{'id': 1, 'name': '中国人'}, {'id': 2, 'name': 'english'}]
```

### Compression

It's possible to adjust compression detection by providing the algorithm explicitly. For the example below it's not required as it would be detected anyway:

```python goodread title="Python"
from frictionless import Resource

with Resource('data/table.csv.zip', compression='zip') as resource:
  print(resource.compression)
  print(resource.read_rows())
```
```
zip
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

### Control

The Control object allows you to manage the loader used by the Resource class. In most cases, you don't need to provide any Control settings but sometimes it can be useful:

```python goodread title="Python"
from frictionless import Resource
from frictionless.plugins.remote import RemoteControl

source = 'https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/table.csv'
control = RemoteControl(http_timeout=10)
with Resource(source, control=control) as resource:
  print(resource.control)
  print(resource.read_rows())
```
```
{'httpTimeout': 10}
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

Exact parameters depend on schemes and can be found in the "Schemes Reference". For example, the Remote Control provides `http_timeout`, `http_session`, and others but there is only one option available for all controls:

### Dialect

The Dialect adjusts the way the parsers work. The concept is similar to the Control above. Let's use the CSV Dialect to adjust the delimiter configuration:

```python goodread title="Python"
from frictionless import Resource
from frictionless.plugins.csv import CsvDialect

source = b'header1;header2\nvalue1;value2'
dialect = CsvDialect(delimiter=';')
with Resource(source, format='csv', dialect=dialect) as resource:
  print(resource.dialect)
  print(resource.read_rows())
```
```
{'delimiter': ';'}
[{'header1': 'value1', 'header2': 'value2'}]
```

There are a great deal of options available for different dialects that can be found in "Formats Reference". We will list the properties that can be used with every dialect:

## Table Details

The core concepts for tabular resource are Layout and Schema.

### Layout

Please read [Layout Guide](layout-guide.md) for more information.

### Schema

Please read [Schema Guide](schema-guide.md) for more information.

### Stats

Resource's stats can be accessed with `resource.stats`:

```python goodread title="Python"
from frictionless import Resource

resource = Resource('data/table.csv')
resource.infer(stats=True)
print(resource.stats)
```
```
{'hash': '6c2c61dd9b0e9c6876139a449ed87933', 'bytes': 30, 'fields': 2, 'rows': 2}
```

## Resource Options

Extraction function and classes accepts a few options that are needed to manage integrity behaviour:

### Basepath

Will make all the paths treated as relative to this path.

### Detector

[Detector](detector-guide.md) object to tweak metadata detection.

### Onerror

This option accept one of the three possible values configuring an `extract`, `Resou`, `Resource` or `Package` behaviour if there is an error during the row reading process:
- ignore (default)
- warn
- raise

Let's investigate how we can add warnings on all header/row errors:

```python title="Python"
from frictionless import Resource

data = [["name"], [1], [2], [3]]
schema = {"fields": [{"name": "name", "type": "string"}]}
with  Resource(data, schema=schema, onerror="warn") as table:
  table.read_rows()
```

    /home/roll/projects/frictionless-py/frictionless/table.py:771: UserWarning: The cell "1" in row at position "2" and field "name" at position "1" has incompatible type: type is "string/default"
      warnings.warn(error.message, UserWarning)
    /home/roll/projects/frictionless-py/frictionless/table.py:771: UserWarning: The cell "2" in row at position "3" and field "name" at position "1" has incompatible type: type is "string/default"
      warnings.warn(error.message, UserWarning)
    /home/roll/projects/frictionless-py/frictionless/table.py:771: UserWarning: The cell "3" in row at position "4" and field "name" at position "1" has incompatible type: type is "string/default"
      warnings.warn(error.message, UserWarning)

In some cases, we need to fail on the first error. We will use `raise` for it:

```python
from frictionless import Resource

data = [["name"], [1], [2], [3]]
schema = {"fields": [{"name": "name", "type": "string"}]}
resource = Resource(data=data, schema=schema)
resource.onerror = 'raise' # for Resource/Package it's possible to set this property after initialization
try:
  resource.read_rows()
except Exception as exception:
  print(exception)
```

    [type-error] The cell "1" in row at position "2" and field "name" at position "1" has incompatible type: type is "string/default"

### Trusted

By default an error will be reaised on [unsafe paths](https://specs.frictionlessdata.io/data-resource/#url-or-path). Setting `trusted` to `True` will disable this behaviour.
