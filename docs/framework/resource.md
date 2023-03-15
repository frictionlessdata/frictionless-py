---
script:
  basepath: data
topics:
  selector: h2
---

# Resource Class

The Resource class is arguable the most important class of the whole Frictionless Framework. It's based on [Data Resource Standard](https://specs.frictionlessdata.io/data-resource/) and  [Tabular Data Resource Standard](https://specs.frictionlessdata.io/data-resource/)

## Creating Resource

Let's create a data resource:

```python tabs=Python
from frictionless import Resource

resource = Resource('table.csv') # from a resource path
resource = Resource('resource.json') # from a descriptor path
resource = Resource({'path': 'table.csv'}) # from a descriptor
resource = Resource(path='table.csv') # from arguments
```

As you can see it's possible to create a resource providing different kinds of sources which will be detector to have some type automatically (e.g. whether it's a descriptor or a path). It's possible to make this step more explicit:

```python tabs=Python
from frictionless import Resource

resource = Resource(path='data/table.csv') # from a path
resource = Resource('data/resource.json') # from a descriptor
```

## Describing Resource

The standards support a great deal of resource metadata which is possible to have with Frictionless Framework too:

```python script tabs=Python
from frictionless import Resource

resource = Resource(
    name='resource',
    title='My Resource',
    description='My Resource for the Guide',
    path='table.csv',
    # it's possible to provide all the official properties like mediatype, etc
)
print(resource)
```

If you have created a resource, for example, from a descriptor you can access this properties:

```python script tabs=Python
from frictionless import Resource

resource = Resource('resource.json')
print(resource.name)
# and others
```

And edit them:

```python script tabs=Python
from frictionless import Resource

resource = Resource('resource.json')
resource.name = 'new-name'
resource.title = 'New Title'
resource.description = 'New Description'
# and others
print(resource)
```

## Saving Descriptor

As any of the Metadata classes the Resource class can be saved as JSON or YAML:

```python tabs=Python
from frictionless import Resource
resource = Resource('table.csv')
resource.to_json('resource.json') # Save as JSON
resource.to_yaml('resource.yaml') # Save as YAML
```

## Resource Lifecycle

You might have noticed that we had to duplicate the `with Resource(...)` statement in some examples. The reason is that Resource is a streaming interface. Once it's read you need to open it again. Let's show it in an example:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource('capital-3.csv')
resource.open()
pprint(resource.read_rows())
pprint(resource.read_rows())
# We need to re-open: there is no data left
resource.open()
pprint(resource.read_rows())
# We need to close manually: not context manager is used
resource.close()
```

At the same you can read data for a resource without opening and closing it explicitly. In this case Frictionless Framework will open and close the resource for you so it will be basically a one-time operation:

```python script tabs=Python
from frictionless import Resource

resource = Resource('capital-3.csv')
pprint(resource.read_rows())
```

## Reading Data

The Resource class is also a metadata class which provides various read and stream functions. The `extract` functions always read rows into memory; Resource can do the same but it also gives a choice regarding output data. It can be `rows`, `data`, `text`, or `bytes`. Let's try reading all of them:

```python script tabs=Python
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_bytes())
pprint(resource.read_text())
pprint(resource.read_cells())
pprint(resource.read_rows())
```

It's really handy to read all your data into memory but it's not always possible if a file is really big. For such cases, Frictionless provides streaming functions:

```python script tabs=Python
from frictionless import Resource

with Resource('country-3.csv') as resource:
    pprint(resource.byte_stream)
    pprint(resource.text_stream)
    pprint(resource.cell_stream)
    pprint(resource.row_stream)
    for row in resource.row_stream:
      print(row)
```

## Indexing Data

```markdown remark type=warning
This functionality has been published in `frictionless@5.5` as a feature preview and request for comments. The implementation is raw and doesn't cover many edge cases.
```

Indexing resource in Frictionless terms means loading a data table into a database. Let's explore how this feature works in different modes.

> All the example are written for SQLite for simplicity

### Normal Mode

This mode is supported for any database that is supported by `sqlalchemy`. Under the hood, Frictionless will infer Table Schema and populate the data table as it normally reads data. It means that type errors will be replaced by `null` values and in-general it guarantees to finish successfully for any data even very invalid.

```bash script tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --name table
frictionless extract sqlite:///index/project.db --table table --json
```

```python script tabs=Python
import sqlite3
from frictionless import Resource, formats

resource = Resource('table.csv')
resource.index('sqlite:///index/project.db', name='table')
print(Resource('sqlite:///index/project.db', control=formats.sql.SqlControl(table='table')).extract())
```

### Fast Mode

```markdown remark type=warning
For the SQLite in fast mode, it requires `sqlite3@3.34+` command to be available.
```

Fast mode is supported for SQLite and Postgresql databases. It will infer Table Schema using a data sample and index data using `COPY` in Potgresql and `.import` in SQLite. For big data files this mode will be 10-30x faster than normal indexing but the speed comes with the price -- if there is invalid data the indexing will fail.

```bash script tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --name table --fast
frictionless extract sqlite:///index/project.db --table table --json
```

```python script tabs=Python
import sqlite3
from frictionless import Resource, formats

resource = Resource('table.csv')
resource.index('sqlite:///index/project.db', name='table', fast=True)
print(Resource('sqlite:///index/project.db', control=formats.sql.SqlControl(table='table')).extract())
```

#### Solution 1: Fallback

To ensure that the data will be successfully indexed it's possible to use `fallback` option. If the fast indexing fails Frictionless will start over in normal mode and finish the process successfully.

```bash tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --name table --fast --fallback
```

```python tabs=Python
import sqlite3
from frictionless import Resource, formats

resource = Resource('table.csv')
resource.index('sqlite:///index/project.db', name='table', fast=True, fallback=True)
```

#### Solution 2: QSV

Another option is to provide a path to [QSV](https://github.com/jqnatividad/qsv) binary. In this case, initial schema inferring will be done based on the whole data file and will guarantee that the table is valid type-wise:

```bash tabs=CLI
frictionless index table.csv --database sqlite:///index/project.db --name table --fast --qsv qsv_path
```

```python tabs=Python
import sqlite3
from frictionless import Resource, formats

resource = Resource('table.csv')
resource.index('sqlite:///index/project.db', name='table', fast=True, qsv_path='qsv_path')
```

## Scheme

The scheme also know as protocol indicates which loader Frictionless should use to read or write data. It can be `file` (default), `text`, `http`, `https`, `s3`, and others.

```python script tabs=Python
from frictionless import Resource

with Resource(b'header1,header2\nvalue1,value2', format='csv') as resource:
  print(resource.scheme)
  print(resource.to_view())
```

## Format

The format or as it's also called extension helps Frictionless to choose a proper parser to handle the file. Popular formats are `csv`, `xlsx`, `json` and others

```python script tabs=Python
from frictionless import Resource

with Resource(b'header1,header2\nvalue1,value2.csv', format='csv') as resource:
  print(resource.format)
  print(resource.to_view())
```

## Encoding

Frictionless automatically detects encoding of files but sometimes it can be inaccurate. It's possible to provide an encoding manually:

```python script tabs=Python
from frictionless import Resource

with Resource('country-3.csv', encoding='utf-8') as resource:
  print(resource.encoding)
  print(resource.path)
```
```
utf-8
data/country-3.csv
```

## Innerpath

By default, Frictionless uses the first file found in a zip archive. It's possible to adjust this behaviour:

```python script tabs=Python
from frictionless import Resource

with Resource('table-multiple-files.zip', innerpath='table-reverse.csv') as resource:
  print(resource.compression)
  print(resource.innerpath)
  print(resource.to_view())
```

## Compression

It's possible to adjust compression detection by providing the algorithm explicitly. For the example below it's not required as it would be detected anyway:

```python script tabs=Python
from frictionless import Resource

with Resource('table.csv.zip', compression='zip') as resource:
  print(resource.compression)
  print(resource.to_view())
```

## Dialect

Please read [Table Dialect Guide](dialect.html) for more information.

## Schema

Please read [Table Schema Guide](schema.html) for more information.

## Checklist

Please read [Checklist Guide](checklist.html) for more information.

## Pipeline

Please read [Pipeline Guide](pipeline.html) for more information.

## Stats

Resource's stats can be accessed with `resource.stats`:

```python script tabs=Python
from frictionless import Resource

resource = Resource('table.csv')
resource.infer(stats=True)
print(resource.stats)
```

## Reference

```yaml reference
references:
  - frictionless.Resource
```
