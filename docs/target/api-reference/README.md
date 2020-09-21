<a name="frictionless"></a>
# API Reference

<a name="frictionless.file"></a>
## frictionless.file

<a name="frictionless.file.File"></a>
### File

```python
class File(Metadata)
```

File representation

API      | Usage
-------- | --------
Public   | `from frictionless import File`

Under the hood, File uses available loaders so it can open from local, remote,
and any other supported schemes. The File class inherits from the Metadata class
all the metadata's functionality


```python
from frictionless import File

with File('data/text.txt') as file:
    file.read_text()
```

**Arguments**:

- `source` _any_ - file source
- `scheme?` _str_ - file scheme
- `format?` _str_ - file format
- `hashing?` _str_ - file hashing
- `encoding?` _str_ - file encoding
- `compression?` _str_ - file compression
- `compression_path?` _str_ - file compression path
- `control?` _dict_ - file control
- `dialect?` _dict_ - table dialect
- `query?` _dict_ - table query
- `newline?` _str_ - python newline e.g. '\n',
- `stats?` _{hash: str, bytes: int, rows: int}_ - stats object
  

**Raises**:

- `FrictionlessException` - if there is a metadata validation error

<a name="frictionless.file.File.path"></a>
#### <big>path</big>

```python
 | @property
 | path()
```

**Returns**:

- `str` - file path

<a name="frictionless.file.File.source"></a>
#### <big>source</big>

```python
 | @Metadata.property
 | source()
```

**Returns**:

- `any` - file source

<a name="frictionless.file.File.scheme"></a>
#### <big>scheme</big>

```python
 | @Metadata.property
 | scheme()
```

**Returns**:

- `str?` - file scheme

<a name="frictionless.file.File.format"></a>
#### <big>format</big>

```python
 | @Metadata.property
 | format()
```

**Returns**:

- `str?` - file format

<a name="frictionless.file.File.hashing"></a>
#### <big>hashing</big>

```python
 | @Metadata.property
 | hashing()
```

**Returns**:

- `str?` - file hashing

<a name="frictionless.file.File.encoding"></a>
#### <big>encoding</big>

```python
 | @Metadata.property
 | encoding()
```

**Returns**:

- `str?` - file encoding

<a name="frictionless.file.File.compression"></a>
#### <big>compression</big>

```python
 | @Metadata.property
 | compression()
```

**Returns**:

- `str?` - file compression

<a name="frictionless.file.File.compression_path"></a>
#### <big>compression\_path</big>

```python
 | @Metadata.property
 | compression_path()
```

**Returns**:

- `str?` - file compression path

<a name="frictionless.file.File.control"></a>
#### <big>control</big>

```python
 | @Metadata.property
 | control()
```

**Returns**:

- `Control?` - file control

<a name="frictionless.file.File.dialect"></a>
#### <big>dialect</big>

```python
 | @Metadata.property
 | dialect()
```

**Returns**:

- `Dialect?` - table dialect

<a name="frictionless.file.File.query"></a>
#### <big>query</big>

```python
 | @Metadata.property
 | query()
```

**Returns**:

- `Query?` - table query

<a name="frictionless.file.File.newline"></a>
#### <big>newline</big>

```python
 | @Metadata.property
 | newline()
```

**Returns**:

- `str?` - file newline

<a name="frictionless.file.File.stats"></a>
#### <big>stats</big>

```python
 | @Metadata.property
 | stats()
```

**Returns**:

- `dict` - file stats

<a name="frictionless.file.File.byte_stream"></a>
#### <big>byte\_stream</big>

```python
 | @Metadata.property(cache=False)
 | byte_stream()
```

File byte stream

The stream is available after opening the file

**Returns**:

- `io.ByteStream` - file byte stream

<a name="frictionless.file.File.text_stream"></a>
#### <big>text\_stream</big>

```python
 | @Metadata.property(cache=False)
 | text_stream()
```

File text stream

The stream is available after opening the file

**Returns**:

- `io.TextStream` - file text stream

<a name="frictionless.file.File.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.file.File.open"></a>
#### <big>open</big>

```python
 | open()
```

Open the file as "io.open" does

<a name="frictionless.file.File.close"></a>
#### <big>close</big>

```python
 | close()
```

Close the file as "filelike.close" does

<a name="frictionless.file.File.closed"></a>
#### <big>closed</big>

```python
 | @property
 | closed()
```

Whether the file is closed

**Returns**:

- `bool` - if closed

<a name="frictionless.file.File.read_bytes"></a>
#### <big>read\_bytes</big>

```python
 | read_bytes()
```

Read bytes from the file

**Returns**:

- `bytes` - file bytes

<a name="frictionless.file.File.read_text"></a>
#### <big>read\_text</big>

```python
 | read_text()
```

Read bytes from the file

**Returns**:

- `str` - file text

<a name="frictionless.file.File.write"></a>
#### <big>write</big>

```python
 | write(target)
```

Write the file to the target

**Arguments**:

- `target` _str_ - target path

<a name="frictionless.pipeline"></a>
## frictionless.pipeline

<a name="frictionless.pipeline.Pipeline"></a>
### Pipeline

```python
class Pipeline(Metadata)
```

Pipeline representation

API      | Usage
-------- | --------
Public   | `from frictionless import Pipeline`

For now, only the `package` type is supported where `steps` should
conform to the `dataflows`s processors. The File class inherits
from the Metadata class all the metadata's functionality



```python
pipeline = Pipeline(
    {
        "type": "package",
        "steps": [
            {"type": "load", "spec": {"loadSource": "data/table.csv"}},
            {"type": "set_type", "spec": {"name": "id", "type": "string"}},
            {"type": "dump_to_path", "spec": {"outPath": tmpdir}},
        ],
    }
)
pipeline.run()
```

**Arguments**:

- `descriptor` _str|dict_ - pipeline descriptor
- `name?` _str_ - pipeline name
- `type?` _str_ - pipeline type
- `steps?` _dict[]_ - pipeline steps

<a name="frictionless.pipeline.Pipeline.name"></a>
#### <big>name</big>

```python
 | @Metadata.property
 | name()
```

**Returns**:

- `str?` - pipeline name

<a name="frictionless.pipeline.Pipeline.type"></a>
#### <big>type</big>

```python
 | @Metadata.property
 | type()
```

**Returns**:

- `str?` - pipeline type

<a name="frictionless.pipeline.Pipeline.steps"></a>
#### <big>steps</big>

```python
 | @Metadata.property
 | steps()
```

**Returns**:

- `dict[]?` - pipeline steps

<a name="frictionless.pipeline.Pipeline.run"></a>
#### <big>run</big>

```python
 | run()
```

Run the pipeline

<a name="frictionless.table"></a>
## frictionless.table

<a name="frictionless.table.Table"></a>
### Table

```python
class Table()
```

Table representation

API      | Usage
-------- | --------
Public   | `from frictionless import Table`

This class is at heart of the whole Frictionless framwork.
It loads a data source, and allows you to stream its parsed contents.


```python
with Table("data/table.csv") as table:
    table.header == ["id", "name"]
    table.read_rows() == [
        {'id': 1, 'name': 'english'},
        {'id': 2, 'name': '中国人'},
    ]
```

**Arguments**:

  
- `source` _any_ - Source of the file; can be in various forms.
  Usually, it's a string as `<scheme>://path/to/file.<format>`.
  It also can be, for example, an array of data arrays/dictionaries.
  
- `scheme?` _str_ - Scheme for loading the file (file, http, ...).
  If not set, it'll be inferred from `source`.
  
- `format?` _str_ - File source's format (csv, xls, ...).
  If not set, it'll be inferred from `source`.
  
- `encoding?` _str_ - An algorithm to hash data.
  It defaults to 'md5'.
  
- `encoding?` _str_ - Source encoding.
  If not set, it'll be inferred from `source`.
  
- `compression?` _str_ - Source file compression (zip, ...).
  If not set, it'll be inferred from `source`.
  
- `compression_path?` _str_ - A path within the compressed file.
  It defaults to the first file in the archive.
  
- `control?` _dict|Control_ - File control.
  For more infromation, please check the Control documentation.
  
- `dialect?` _dict|Dialect_ - Table dialect.
  For more infromation, please check the Dialect documentation.
  
- `query?` _dict|Query_ - Table query.
  For more infromation, please check the Query documentation.
  
- `headers?` _int|int[]|[int[], str]_ - Either a row
  number or list of row numbers (in case of multi-line headers) to be
  considered as headers (rows start counting at 1), or a pair
  where the first element is header rows and the second the
  header joiner.  It defaults to 1.
  
- `schema?` _dict|Schema_ - Table schema.
  For more infromation, please check the Schema documentation.
  
- `sync_schema?` _bool_ - Whether to sync the schema.
  If it sets to `True` the provided schema will be mapped to
  the inferred schema. It means that, for example, you can
  provide a subset of fileds to be applied on top of the inferred
  fields or the provided schema can have different order of fields.
  
- `patch_schema?` _dict_ - A dictionary to be used as an inferred schema patch.
  The form of this dictionary should follow the Schema descriptor form
  except for the `fields` property which should be a mapping with the
  key named after a field name and the values being a field patch.
  For more information, please check "Extracting Data" guide.
  
- `infer_type?` _str_ - Enforce all the inferred types to be this type.
  For more information, please check "Describing  Data" guide.
  
- `infer_names?` _str[]_ - Enforce all the inferred fields to have provided names.
  For more information, please check "Describing  Data" guide.
  
- `infer_volume?` _int_ - The amount of rows to be extracted as a samle.
  For more information, please check "Describing  Data" guide.
  It defaults to 100
  
- `infer_confidence?` _float_ - A number from 0 to 1 setting the infer confidence.
  If  1 the data is guaranteed to be valid against the inferred schema.
  For more information, please check "Describing  Data" guide.
  It defaults to 0.9
  
- `infer_missing_values?` _str[]_ - String to be considered as missing values.
  For more information, please check "Describing  Data" guide.
  It defaults to `['']`
  
- `lookup?` _dict_ - The lookup is a special object providing relational information.
  For more information, please check "Extracting  Data" guide.

<a name="frictionless.table.Table.path"></a>
#### <big>path</big>

```python
 | @property
 | path()
```

**Returns**:

- `str` - file path

<a name="frictionless.table.Table.source"></a>
#### <big>source</big>

```python
 | @property
 | source()
```

**Returns**:

- `any` - file source

<a name="frictionless.table.Table.scheme"></a>
#### <big>scheme</big>

```python
 | @property
 | scheme()
```

**Returns**:

- `str?` - file scheme

<a name="frictionless.table.Table.format"></a>
#### <big>format</big>

```python
 | @property
 | format()
```

**Returns**:

- `str?` - file format

<a name="frictionless.table.Table.hashing"></a>
#### <big>hashing</big>

```python
 | @property
 | hashing()
```

**Returns**:

- `str?` - file hashing

<a name="frictionless.table.Table.encoding"></a>
#### <big>encoding</big>

```python
 | @property
 | encoding()
```

**Returns**:

- `str?` - file encoding

<a name="frictionless.table.Table.compression"></a>
#### <big>compression</big>

```python
 | @property
 | compression()
```

**Returns**:

- `str?` - file compression

<a name="frictionless.table.Table.compression_path"></a>
#### <big>compression\_path</big>

```python
 | @property
 | compression_path()
```

**Returns**:

- `str?` - file compression path

<a name="frictionless.table.Table.control"></a>
#### <big>control</big>

```python
 | @property
 | control()
```

**Returns**:

- `Control?` - file control

<a name="frictionless.table.Table.query"></a>
#### <big>query</big>

```python
 | @property
 | query()
```

**Returns**:

- `Query?` - table query

<a name="frictionless.table.Table.dialect"></a>
#### <big>dialect</big>

```python
 | @property
 | dialect()
```

**Returns**:

- `Dialect?` - table dialect

<a name="frictionless.table.Table.schema"></a>
#### <big>schema</big>

```python
 | @property
 | schema()
```

**Returns**:

- `Schema?` - table schema

<a name="frictionless.table.Table.header"></a>
#### <big>header</big>

```python
 | @property
 | header()
```

**Returns**:

- `str[]?` - table header

<a name="frictionless.table.Table.sample"></a>
#### <big>sample</big>

```python
 | @property
 | sample()
```

Tables's rows used as sample.

These sample rows are used internally to infer characteristics of the
source file (e.g. schema, ...).

**Returns**:

- `list[]?` - table sample

<a name="frictionless.table.Table.stats"></a>
#### <big>stats</big>

```python
 | @property
 | stats()
```

Table stats

The stats object has:
- hash: str - hashing sum
- bytes: int - number of bytes
- rows: int - number of rows

**Returns**:

- `dict?` - table stats

<a name="frictionless.table.Table.data_stream"></a>
#### <big>data\_stream</big>

```python
 | @property
 | data_stream()
```

Data stream in form of a generator of data arrays

**Yields**:

- `any[][]?` - data stream

<a name="frictionless.table.Table.row_stream"></a>
#### <big>row\_stream</big>

```python
 | @property
 | row_stream()
```

Row stream in form of a generator of Row objects

**Yields**:

- `Row[][]?` - row stream

<a name="frictionless.table.Table.open"></a>
#### <big>open</big>

```python
 | open()
```

Open the table as "io.open" does

**Raises**:

- `FrictionlessException` - any exception that occurs

<a name="frictionless.table.Table.close"></a>
#### <big>close</big>

```python
 | close()
```

Close the table as "filelike.close" does

<a name="frictionless.table.Table.closed"></a>
#### <big>closed</big>

```python
 | @property
 | closed()
```

Whether the table is closed

**Returns**:

- `bool` - if closed

<a name="frictionless.table.Table.read_data"></a>
#### <big>read\_data</big>

```python
 | read_data()
```

Read data stream into memory

**Returns**:

- `any[][]` - table data

<a name="frictionless.table.Table.read_rows"></a>
#### <big>read\_rows</big>

```python
 | read_rows()
```

Read row stream into memory

**Returns**:

- `Row[][]` - table rows

<a name="frictionless.table.Table.write"></a>
#### <big>write</big>

```python
 | write(target, *, scheme=None, format=None, hashing=None, encoding=None, compression=None, compression_path=None, control=None, dialect=None)
```

Write the table to the target

**Arguments**:

- `target` _str_ - target path
- `**options` - subset of Table's constructor options

<a name="frictionless.row"></a>
## frictionless.row

<a name="frictionless.row.Row"></a>
### Row

```python
class Row(OrderedDict)
```

Row representation

API      | Usage
-------- | --------
Public   | `from frictionless import Table`

This object is returned by `extract`, `table.read_rows`, and other functions.


```python
rows = extract("data/table.csv")
for row in rows:
    # work with the Row
```

**Arguments**:

- `cells` _any[]_ - array of cells
- `schema` _Schema_ - table schema
- `field_positions` _int[]_ - table field positions
- `row_position` _int_ - row position from 1
- `row_number` _int_ - row number from 1

<a name="frictionless.row.Row.schema"></a>
#### <big>schema</big>

```python
 | @cached_property
 | schema()
```

**Returns**:

- `Schema` - table schema

<a name="frictionless.row.Row.field_positions"></a>
#### <big>field\_positions</big>

```python
 | @cached_property
 | field_positions()
```

**Returns**:

- `int[]` - table field positions

<a name="frictionless.row.Row.row_position"></a>
#### <big>row\_position</big>

```python
 | @cached_property
 | row_position()
```

**Returns**:

- `int` - row position from 1

<a name="frictionless.row.Row.row_number"></a>
#### <big>row\_number</big>

```python
 | @cached_property
 | row_number()
```

**Returns**:

- `int` - row number from 1

<a name="frictionless.row.Row.blank_cells"></a>
#### <big>blank\_cells</big>

```python
 | @cached_property
 | blank_cells()
```

A mapping indexed by a field name with blank cells before parsing

**Returns**:

- `dict` - row blank cells

<a name="frictionless.row.Row.error_cells"></a>
#### <big>error\_cells</big>

```python
 | @cached_property
 | error_cells()
```

A mapping indexed by a field name with error cells before parsing

**Returns**:

- `dict` - row error cells

<a name="frictionless.row.Row.errors"></a>
#### <big>errors</big>

```python
 | @cached_property
 | errors()
```

**Returns**:

- `Error[]` - row errors

<a name="frictionless.row.Row.valid"></a>
#### <big>valid</big>

```python
 | @cached_property
 | valid()
```

**Returns**:

- `bool` - if row valid

<a name="frictionless.row.Row.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(*, json=False)
```

**Arguments**:

- `json` _bool_ - make data types compatible with JSON format
  

**Returns**:

- `dict` - a row as a dictionary

<a name="frictionless.row.Row.to_list"></a>
#### <big>to\_list</big>

```python
 | to_list(*, json=False)
```

**Arguments**:

- `json` _bool_ - make data types compatible with JSON format
  

**Returns**:

- `dict` - a row as a list

<a name="frictionless.checks"></a>
## frictionless.checks

<a name="frictionless.checks.checksum"></a>
## frictionless.checks.checksum

<a name="frictionless.checks.checksum.ChecksumCheck"></a>
### ChecksumCheck

```python
class ChecksumCheck(Check)
```

Check a table's checksum

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(checksum={...})`

Ths check is enabled by default if the `checksum` argument
is provided for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `descriptor.hash?` _str_ - a hash sum of the table's bytes
- `descriptor.bytes?` _int_ - number of bytes
- `descriptor.rows?` _int_ - number of rows

<a name="frictionless.checks.regulation"></a>
## frictionless.checks.regulation

<a name="frictionless.checks.regulation.BlacklistedValueCheck"></a>
### BlacklistedValueCheck

```python
class BlacklistedValueCheck(Check)
```

Check for blacklisted values in a field

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(extra_checks=[('backlisted-value', {...})])`

This check can be enabled using the `extra_checks` parameter
for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `descriptor.fieldName` _str_ - a field name to look into
- `descriptor.blacklist` _any[]_ - a list of forbidden values

<a name="frictionless.checks.regulation.SequentialValueCheck"></a>
### SequentialValueCheck

```python
class SequentialValueCheck(Check)
```

Check that a column having sequential values

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(extra_checks=[('sequential-value', {...})])`

This check can be enabled using the `extra_checks` parameter
for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `descriptor.fieldName` _str_ - a field name to check

<a name="frictionless.checks.regulation.RowConstraintCheck"></a>
### RowConstraintCheck

```python
class RowConstraintCheck(Check)
```

Check that every row satisfies a provided Python expression

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(extra_checks=(['row-constraint', {...})])`

This check can be enabled using the `extra_checks` parameter
for the `validate` function. The syntax for the row constraint
check can be found here - https://github.com/danthedeckie/simpleeval

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `descriptor.constraint` _str_ - a python expression to evaluate against a row

<a name="frictionless.checks.baseline"></a>
## frictionless.checks.baseline

<a name="frictionless.checks.baseline.BaselineCheck"></a>
### BaselineCheck

```python
class BaselineCheck(Check)
```

Check a table for basic errors

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(...)`

Ths check is enabled by default for any `validate` function run.

<a name="frictionless.checks.heuristic"></a>
## frictionless.checks.heuristic

<a name="frictionless.checks.heuristic.DuplicateRowCheck"></a>
### DuplicateRowCheck

```python
class DuplicateRowCheck(Check)
```

Check for duplicate rows

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(extra_checks=['duplicate-row'])`

This check can be enabled using the `extra_checks` parameter
for the `validate` function.

<a name="frictionless.checks.heuristic.DeviatedValueCheck"></a>
### DeviatedValueCheck

```python
class DeviatedValueCheck(Check)
```

Check for deviated values in a field

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(extra_checks=(['deviated-values', {...})])`

This check can be enabled using the `extra_checks` parameter
for the `validate` function.

**Arguments**:

- `descriptor` _dict_ - check's descriptor
- `descriptor.fieldName` _str_ - a field name to check
- `descriptor.average?` _str_ - one of `main`, `median` or `mode`
- `descriptor.interval?` _str_ - statistical interval (default: 3)

<a name="frictionless.checks.heuristic.TruncatedValueCheck"></a>
### TruncatedValueCheck

```python
class TruncatedValueCheck(Check)
```

Check for possible truncated values

API      | Usage
-------- | --------
Public   | `from frictionless import checks`
Implicit | `validate(extra_checks=(['truncated-value', {...})])`

This check can be enabled using the `extra_checks` parameter
for the `validate` function.

<a name="frictionless.package"></a>
## frictionless.package

<a name="frictionless.package.Package"></a>
### Package

```python
class Package(Metadata)
```

Package representation

API      | Usage
-------- | --------
Public   | `from frictionless import Package`


```python
package = Package(resources=[Resource(path="data/table.csv")])
package.get_resoure('table').read_rows() == [
    {'id': 1, 'name': 'english'},
    {'id': 2, 'name': '中国人'},
]
```

**Arguments**:

- `descriptor?` _str|dict_ - package descriptor
- `name?` _str_ - package name (for machines)
- `title?` _str_ - package title (for humans)
- `descriptor?` _str_ - package descriptor
- `resources?` _dict|Resource[]_ - list of resource descriptors
- `profile?` _str_ - profile name like 'data-package'
- `basepath?` _str_ - a basepath of the package
- `trusted?` _bool_ - don't raise on unsafe paths
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.package.Package.name"></a>
#### <big>name</big>

```python
 | @Metadata.property
 | name()
```

**Returns**:

- `str?` - package name

<a name="frictionless.package.Package.title"></a>
#### <big>title</big>

```python
 | @Metadata.property
 | title()
```

**Returns**:

- `str?` - package title

<a name="frictionless.package.Package.description"></a>
#### <big>description</big>

```python
 | @Metadata.property
 | description()
```

**Returns**:

- `str?` - package description

<a name="frictionless.package.Package.basepath"></a>
#### <big>basepath</big>

```python
 | @Metadata.property(write=False)
 | basepath()
```

**Returns**:

- `str` - package basepath

<a name="frictionless.package.Package.profile"></a>
#### <big>profile</big>

```python
 | @Metadata.property
 | profile()
```

**Returns**:

- `str` - package profile

<a name="frictionless.package.Package.resources"></a>
#### <big>resources</big>

```python
 | @Metadata.property
 | resources()
```

**Returns**:

- `Resources[]` - package resource

<a name="frictionless.package.Package.resource_names"></a>
#### <big>resource\_names</big>

```python
 | @Metadata.property(write=False)
 | resource_names()
```

**Returns**:

- `str[]` - package resource names

<a name="frictionless.package.Package.add_resource"></a>
#### <big>add\_resource</big>

```python
 | add_resource(descriptor)
```

Add new resource to package.

**Arguments**:

- `descriptor` _dict_ - resource descriptor
  

**Returns**:

- `Resource/None` - added `Resource` instance or `None` if not added

<a name="frictionless.package.Package.get_resource"></a>
#### <big>get\_resource</big>

```python
 | get_resource(name)
```

Get resource by name.

**Arguments**:

- `name` _str_ - resource name
  

**Returns**:

- `Resource/None` - `Resource` instance or `None` if not found

<a name="frictionless.package.Package.has_resource"></a>
#### <big>has\_resource</big>

```python
 | has_resource(name)
```

Check if a resource is present

**Arguments**:

- `name` _str_ - schema resource name
  

**Returns**:

- `bool` - whether there is the resource

<a name="frictionless.package.Package.remove_resource"></a>
#### <big>remove\_resource</big>

```python
 | remove_resource(name)
```

Remove resource by name.

**Arguments**:

- `name` _str_ - resource name
  

**Returns**:

- `Resource/None` - removed `Resource` instances or `None` if not found

<a name="frictionless.package.Package.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

It will add default values to the package.

<a name="frictionless.package.Package.infer"></a>
#### <big>infer</big>

```python
 | infer(source=None, *, only_sample=False)
```

Infer package's attributes

**Arguments**:

- `source` _str|str[]_ - path, list of paths or glob pattern
- `only_sample?` _bool_ - infer whatever possible but only from the sample

<a name="frictionless.package.Package.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert package to a dict

**Arguments**:

- `expand?` _bool_ - return expanded metadata
  

**Returns**:

- `dict` - package as a dict

<a name="frictionless.package.Package.to_zip"></a>
#### <big>to\_zip</big>

```python
 | to_zip(target)
```

Save package to a zip

**Arguments**:

- `target` _str_ - target path
  

**Raises**:

- `FrictionlessException` - on any error

<a name="frictionless.plugin"></a>
## frictionless.plugin

<a name="frictionless.plugin.Plugin"></a>
### Plugin

```python
class Plugin()
```

Plugin representation

API      | Usage
-------- | --------
Public   | `from frictionless import Plugin`

It's an interface for writing Frictionless plugins.
You can implement one or more methods to hook into Frictionless system.

<a name="frictionless.plugin.Plugin.create_check"></a>
#### <big>create\_check</big>

```python
 | create_check(name, *, descriptor=None)
```

Create checks

**Arguments**:

- `name` _str_ - check name
- `descriptor` _dict_ - check descriptor
  

**Returns**:

- `Check` - check

<a name="frictionless.plugin.Plugin.create_control"></a>
#### <big>create\_control</big>

```python
 | create_control(file, *, descriptor)
```

Create control

**Arguments**:

- `file` _File_ - control file
- `descriptor` _dict_ - control descriptor
  

**Returns**:

- `Control` - control

<a name="frictionless.plugin.Plugin.create_dialect"></a>
#### <big>create\_dialect</big>

```python
 | create_dialect(file, *, descriptor)
```

Create dialect

**Arguments**:

- `file` _File_ - dialect file
- `descriptor` _dict_ - dialect descriptor
  

**Returns**:

- `Dialect` - dialect

<a name="frictionless.plugin.Plugin.create_loader"></a>
#### <big>create\_loader</big>

```python
 | create_loader(file)
```

Create loader

**Arguments**:

- `file` _File_ - loader file
  

**Returns**:

- `Loader` - loader

<a name="frictionless.plugin.Plugin.create_parser"></a>
#### <big>create\_parser</big>

```python
 | create_parser(file)
```

Create parser

**Arguments**:

- `file` _File_ - parser file
  

**Returns**:

- `Parser` - parser

<a name="frictionless.plugin.Plugin.create_server"></a>
#### <big>create\_server</big>

```python
 | create_server(name)
```

Create server

**Arguments**:

- `name` _str_ - server name
  

**Returns**:

- `Server` - server

<a name="frictionless.program"></a>
## frictionless.program

<a name="frictionless.program.main"></a>
## frictionless.program.main

<a name="frictionless.program.main.program"></a>
#### <big>program</big>

```python
@click.group(name="frictionless")
@click.version_option(config.VERSION, message="%(version)s", help="Print version")
program()
```

Main program

API      | Usage
-------- | --------
Public   | `$ frictionless`

<a name="frictionless.program.validate"></a>
## frictionless.program.validate

<a name="frictionless.program.validate.program_validate"></a>
#### <big>program\_validate</big>

```python
@program.command(name="validate")
@click.argument("source", type=click.Path(), nargs=-1, required=True)
@click.option("--source-type", type=str, help="Source type")
@click.option("--json", is_flag=True, help="Output report as JSON")
@click.option("--scheme", type=str, help="File scheme")
@click.option("--format", type=str, help="File format")
@click.option("--hashing", type=str, help="File hashing")
@click.option("--encoding", type=str, help="File encoding")
@click.option("--compression", type=str, help="File compression")
@click.option("--compression-path", type=str, help="File compression path")
@click.option("--headers", type=int, multiple=True, help="Headers")
@click.option("--schema", type=click.Path(), help="Schema")
@click.option("--sync-schema", is_flag=True, help="Sync schema")
@click.option("--infer-type", type=str, help="Infer type")
@click.option("--infer-names", type=str, multiple=True, help="Infer names")
@click.option("--infer-sample", type=int, help="Infer sample")
@click.option("--infer-confidence", type=float, help="Infer confidence")
@click.option("--infer-missing-values", type=str, multiple=True, help="Infer missing")
@click.option("--checksum-hash", type=str, help="Expected hash based on hashing option")
@click.option("--checksum-bytes", type=int, help="Expected size in bytes")
@click.option("--checksum-rows", type=int, help="Expected size in bytes")
@click.option("--pick-errors", type=str, multiple=True, help="Pick errors")
@click.option("--skip-errors", type=str, multiple=True, help="Skip errors")
@click.option("--limit-errors", type=int, help="Limit errors")
@click.option("--limit-memory", type=int, help="Limit memory")
@click.option("--noinfer", type=bool, help="Validate metadata as it is")
program_validate(source, *, source_type, json, **options)
```

Validate data

API      | Usage
-------- | --------
Public   | `$ frictionless validate`

<a name="frictionless.program.transform"></a>
## frictionless.program.transform

<a name="frictionless.program.transform.program_transform"></a>
#### <big>program\_transform</big>

```python
@program.command(name="transform")
@click.argument("source", type=click.Path(), required=True)
program_transform(source)
```

Transform data

API      | Usage
-------- | --------
Public   | `$ frictionless transform`

<a name="frictionless.program.describe"></a>
## frictionless.program.describe

<a name="frictionless.program.describe.program_describe"></a>
#### <big>program\_describe</big>

```python
@program.command(name="describe")
@click.argument("source", type=click.Path(), nargs=-1, required=True)
@click.option("--source-type", type=str, help="Source type")
@click.option("--json", is_flag=True, help="Output report as JSON")
@click.option("--scheme", type=str, help="File scheme")
@click.option("--format", type=str, help="File format")
@click.option("--hashing", type=str, help="File hashing")
@click.option("--encoding", type=str, help="File encoding")
@click.option("--compression", type=str, help="File compression")
@click.option("--compression-path", type=str, help="File compression path")
@click.option("--sync-schema", is_flag=True, help="Sync schema")
@click.option("--infer-type", type=str, help="Infer type")
@click.option("--infer-names", type=str, multiple=True, help="Infer names")
@click.option("--infer-sample", type=int, help="Infer sample")
@click.option("--infer-confidence", type=float, help="Infer confidence")
@click.option("--infer-missing-values", type=str, multiple=True, help="Infer missing")
program_describe(source, *, source_type, json, **options)
```

Describe data

API      | Usage
-------- | --------
Public   | `$ frictionless describe`

<a name="frictionless.program.api"></a>
## frictionless.program.api

<a name="frictionless.program.api.program_api"></a>
#### <big>program\_api</big>

```python
@program.command(name="api")
@click.option("--port", type=int, default=config.DEFAULT_SERVER_PORT, help="Server port")
program_api(port)
```

Start API

API      | Usage
-------- | --------
Public   | `$ frictionless api`

<a name="frictionless.program.extract"></a>
## frictionless.program.extract

<a name="frictionless.program.extract.program_extract"></a>
#### <big>program\_extract</big>

```python
@program.command(name="extract")
@click.argument("source", type=click.Path(), nargs=-1, required=True)
@click.option("--source-type", type=str, help="Source type")
@click.option("--json", is_flag=True, help="Output report as JSON")
@click.option("--scheme", type=str, help="File scheme")
@click.option("--format", type=str, help="File format")
@click.option("--hashing", type=str, help="File hashing")
@click.option("--encoding", type=str, help="File encoding")
@click.option("--compression", type=str, help="File compression")
@click.option("--compression-path", type=str, help="File compression path")
@click.option("--sync-schema", is_flag=True, help="Sync schema")
@click.option("--infer-type", type=str, help="Infer type")
@click.option("--infer-names", type=str, multiple=True, help="Infer names")
@click.option("--infer-sample", type=int, help="Infer sample")
@click.option("--infer-confidence", type=float, help="Infer confidence")
@click.option("--infer-missing-values", type=str, multiple=True, help="Infer missing")
program_extract(source, *, source_type, json, **options)
```

Extract data

API      | Usage
-------- | --------
Public   | `$ frictionless extract`

<a name="frictionless.type"></a>
## frictionless.type

<a name="frictionless.type.Type"></a>
### Type

```python
class Type()
```

Data type representation

API      | Usage
-------- | --------
Public   | `from frictionless import Type`

This class is for subclassing.

**Arguments**:

- `field` _Field_ - field

<a name="frictionless.type.Type.supported_constraints"></a>
#### <big>supported\_constraints</big>

**Returns**:

- `str[]` - a list of supported constraints

<a name="frictionless.type.Type.field"></a>
#### <big>field</big>

```python
 | @cached_property
 | field()
```

**Returns**:

- `Field` - field

<a name="frictionless.type.Type.read_cell"></a>
#### <big>read\_cell</big>

```python
 | read_cell(cell)
```

Convert cell (read direction)

**Arguments**:

- `cell` _any_ - cell to covert
  

**Returns**:

- `any` - converted cell

<a name="frictionless.type.Type.write_cell"></a>
#### <big>write\_cell</big>

```python
 | write_cell(cell)
```

Convert cell (write direction)

**Arguments**:

- `cell` _any_ - cell to covert
  

**Returns**:

- `any` - converted cell

<a name="frictionless.metadata"></a>
## frictionless.metadata

<a name="frictionless.metadata.Metadata"></a>
### Metadata

```python
class Metadata(helpers.ControlledDict)
```

Metadata representation

API      | Usage
-------- | --------
Public   | `from frictionless import Metadata`

**Arguments**:

- `descriptor?` _str|dict_ - metadata descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.metadata.Metadata.metadata_valid"></a>
#### <big>metadata\_valid</big>

```python
 | @property
 | metadata_valid()
```

**Returns**:

- `bool` - whether the metadata is valid

<a name="frictionless.metadata.Metadata.metadata_errors"></a>
#### <big>metadata\_errors</big>

```python
 | @property
 | metadata_errors()
```

**Returns**:

- `Errors[]` - a list of the metadata errors

<a name="frictionless.metadata.Metadata.setinitial"></a>
#### <big>setinitial</big>

```python
 | setinitial(key, value)
```

Set an initial item in a subclass' constructor

**Arguments**:

- `key` _str_ - key
- `value` _any_ - value

<a name="frictionless.metadata.Metadata.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict()
```

Convert metadata to a dict

**Returns**:

- `dict` - metadata as a dict

<a name="frictionless.metadata.Metadata.to_json"></a>
#### <big>to\_json</big>

```python
 | to_json(target=None)
```

Save metadata as a json

**Arguments**:

- `target` _str_ - target path
  

**Raises**:

- `FrictionlessException` - on any error

<a name="frictionless.metadata.Metadata.to_yaml"></a>
#### <big>to\_yaml</big>

```python
 | to_yaml(target=None)
```

Save metadata as a yaml

**Arguments**:

- `target` _str_ - target path
  

**Raises**:

- `FrictionlessException` - on any error

<a name="frictionless.metadata.Metadata.metadata_attach"></a>
#### <big>metadata\_attach</big>

```python
 | metadata_attach(name, value)
```

Helper method for attaching a value to  the metadata

**Arguments**:

- `name` _str_ - name
- `value` _any_ - value

<a name="frictionless.metadata.Metadata.metadata_extract"></a>
#### <big>metadata\_extract</big>

```python
 | metadata_extract(descriptor)
```

Helper method called during the metadata extraction

**Arguments**:

- `descriptor` _any_ - descriptor

<a name="frictionless.metadata.Metadata.metadata_process"></a>
#### <big>metadata\_process</big>

```python
 | metadata_process()
```

Helper method called on any metadata change

<a name="frictionless.metadata.Metadata.metadata_validate"></a>
#### <big>metadata\_validate</big>

```python
 | metadata_validate(profile=None)
```

Helper method called on any metadata change

**Arguments**:

- `profile` _dict_ - a profile to validate against of

<a name="frictionless.metadata.Metadata.property"></a>
#### <big>property</big>

```python
 | @staticmethod
 | property(func=None, *, cache=True, reset=True, write=True)
```

Create a metadata property

**Arguments**:

- `func` _func_ - method
- `cache?` _bool_ - cache
- `reset?` _bool_ - reset
- `write?` _func_ - write

<a name="frictionless.field"></a>
## frictionless.field

<a name="frictionless.field.Field"></a>
### Field

```python
class Field(Metadata)
```

Field representation

API      | Usage
-------- | --------
Public   | `from frictionless import Field`

**Arguments**:

- `descriptor?` _str|dict_ - field descriptor
- `name?` _str_ - field name (for machines)
- `title?` _str_ - field title (for humans)
- `descriptor?` _str_ - field descriptor
- `type?` _str_ - field type e.g. `string`
- `format?` _str_ - field format e.g. `default`
- `missing_values?` _str[]_ - missing values
- `constraints?` _dict_ - constraints
- `schema?` _Schema_ - parent schema object
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.field.Field.name"></a>
#### <big>name</big>

```python
 | @Metadata.property
 | name()
```

**Returns**:

- `str` - name

<a name="frictionless.field.Field.title"></a>
#### <big>title</big>

```python
 | @Metadata.property
 | title()
```

**Returns**:

- `str?` - title

<a name="frictionless.field.Field.description"></a>
#### <big>description</big>

```python
 | @Metadata.property
 | description()
```

**Returns**:

- `str?` - description

<a name="frictionless.field.Field.type"></a>
#### <big>type</big>

```python
 | @Metadata.property
 | type()
```

**Returns**:

- `str` - type

<a name="frictionless.field.Field.format"></a>
#### <big>format</big>

```python
 | @Metadata.property
 | format()
```

**Returns**:

- `str` - format

<a name="frictionless.field.Field.missing_values"></a>
#### <big>missing\_values</big>

```python
 | @Metadata.property
 | missing_values()
```

**Returns**:

- `str[]` - missing values

<a name="frictionless.field.Field.constraints"></a>
#### <big>constraints</big>

```python
 | @Metadata.property
 | constraints()
```

**Returns**:

- `dict` - constraints

<a name="frictionless.field.Field.required"></a>
#### <big>required</big>

```python
 | @Metadata.property(
 |         write=lambda self, value: setitem(self.constraints, "required", value)
 |     )
 | required()
```

**Returns**:

- `bool` - if field is requried

<a name="frictionless.field.Field.true_values"></a>
#### <big>true\_values</big>

```python
 | @Metadata.property
 | true_values()
```

**Returns**:

- `str[]` - true values

<a name="frictionless.field.Field.false_values"></a>
#### <big>false\_values</big>

```python
 | @Metadata.property
 | false_values()
```

**Returns**:

- `str[]` - false values

<a name="frictionless.field.Field.bare_number"></a>
#### <big>bare\_number</big>

```python
 | @Metadata.property
 | bare_number()
```

**Returns**:

- `bool` - if a bare number

<a name="frictionless.field.Field.decimal_char"></a>
#### <big>decimal\_char</big>

```python
 | @Metadata.property
 | decimal_char()
```

**Returns**:

- `str` - decimal char

<a name="frictionless.field.Field.group_char"></a>
#### <big>group\_char</big>

```python
 | @Metadata.property
 | group_char()
```

**Returns**:

- `str` - group char

<a name="frictionless.field.Field.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.field.Field.read_cell"></a>
#### <big>read\_cell</big>

```python
 | read_cell(cell)
```

Read cell (cast)

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

  (any, OrderedDict): processed cell and dict of notes

<a name="frictionless.field.Field.read_cell_cast"></a>
#### <big>read\_cell\_cast</big>

```python
 | read_cell_cast(cell)
```

Read cell low-level (cast)

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

- `any/None` - processed cell or None if an error

<a name="frictionless.field.Field.read_cell_checks"></a>
#### <big>read\_cell\_checks</big>

```python
 | @Metadata.property(write=False)
 | read_cell_checks()
```

Read cell low-level (cast)

**Returns**:

- `OrderedDict` - dictionlary of check function by a constraint name

<a name="frictionless.field.Field.write_cell"></a>
#### <big>write\_cell</big>

```python
 | write_cell(cell)
```

Write cell (cast)

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

  (any, OrderedDict): processed cell and dict of notes

<a name="frictionless.field.Field.write_cell_cast"></a>
#### <big>write\_cell\_cast</big>

```python
 | write_cell_cast(cell)
```

Write cell low-level (cast)

**Arguments**:

- `cell` _any_ - cell
  

**Returns**:

- `any/None` - processed cell or None if an error

<a name="frictionless.field.Field.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert field to dict

**Arguments**:

- `expand` _bool_ - whether to expand

<a name="frictionless.query"></a>
## frictionless.query

<a name="frictionless.query.Query"></a>
### Query

```python
class Query(Metadata)
```

Query representation

API      | Usage
-------- | --------
Public   | `from frictionless import Query`

**Arguments**:

- `descriptor?` _str|dict_ - query descriptor
  pick_fields? ((str|int)[]): what fields to pick
  skip_fields? ((str|int)[]): what fields to skip
- `limit_fields?` _int_ - amount of fields
- `offset_fields?` _int_ - from what field to start
  pick_rows? ((str|int)[]): what rows to pick
  skip_rows? ((str|int)[]): what rows to skip
- `limit_rows?` _int_ - amount of rows
- `offset_rows?` _int_ - from what row to start

<a name="frictionless.query.Query.pick_fields"></a>
#### <big>pick\_fields</big>

```python
 | @Metadata.property
 | pick_fields()
```

**Returns**:

- `(str|int)[]?` - pick fields

<a name="frictionless.query.Query.skip_fields"></a>
#### <big>skip\_fields</big>

```python
 | @Metadata.property
 | skip_fields()
```

**Returns**:

- `(str|int)[]?` - skip fields

<a name="frictionless.query.Query.limit_fields"></a>
#### <big>limit\_fields</big>

```python
 | @Metadata.property
 | limit_fields()
```

**Returns**:

- `int?` - limit fields

<a name="frictionless.query.Query.offset_fields"></a>
#### <big>offset\_fields</big>

```python
 | @Metadata.property
 | offset_fields()
```

**Returns**:

- `int?` - offset fields

<a name="frictionless.query.Query.pick_rows"></a>
#### <big>pick\_rows</big>

```python
 | @Metadata.property
 | pick_rows()
```

**Returns**:

- `(str|int)[]?` - pick rows

<a name="frictionless.query.Query.skip_rows"></a>
#### <big>skip\_rows</big>

```python
 | @Metadata.property
 | skip_rows()
```

**Returns**:

- `(str|int)[]?` - skip rows

<a name="frictionless.query.Query.limit_rows"></a>
#### <big>limit\_rows</big>

```python
 | @Metadata.property
 | limit_rows()
```

**Returns**:

- `int?` - limit rows

<a name="frictionless.query.Query.offset_rows"></a>
#### <big>offset\_rows</big>

```python
 | @Metadata.property
 | offset_rows()
```

**Returns**:

- `int?` - offset rows

<a name="frictionless.query.Query.is_field_filtering"></a>
#### <big>is\_field\_filtering</big>

```python
 | @Metadata.property(write=False)
 | is_field_filtering()
```

**Returns**:

- `bool` - whether there is a field filtering

<a name="frictionless.query.Query.pick_fields_compiled"></a>
#### <big>pick\_fields\_compiled</big>

```python
 | @Metadata.property(write=False)
 | pick_fields_compiled()
```

**Returns**:

- `re?` - compiled pick fields

<a name="frictionless.query.Query.skip_fields_compiled"></a>
#### <big>skip\_fields\_compiled</big>

```python
 | @Metadata.property(write=False)
 | skip_fields_compiled()
```

**Returns**:

- `re?` - compiled skip fields

<a name="frictionless.query.Query.pick_rows_compiled"></a>
#### <big>pick\_rows\_compiled</big>

```python
 | @Metadata.property(write=False)
 | pick_rows_compiled()
```

**Returns**:

- `re?` - compiled pick rows

<a name="frictionless.query.Query.skip_rows_compiled"></a>
#### <big>skip\_rows\_compiled</big>

```python
 | @Metadata.property(write=False)
 | skip_rows_compiled()
```

**Returns**:

- `re?` - compiled skip fields

<a name="frictionless.query.Query.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.query.Query.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert query to dict

**Arguments**:

- `expand` _bool_ - whether to expand

<a name="frictionless.system"></a>
## frictionless.system

<a name="frictionless.system.System"></a>
### System

```python
class System()
```

System representation

API      | Usage
-------- | --------
Public   | `from frictionless import system`

This class provides an ability to make system Frictionless calls.
It's available as `frictionless.system` singletone.

<a name="frictionless.system.System.create_check"></a>
#### <big>create\_check</big>

```python
 | create_check(name, *, descriptor=None)
```

Create checks

**Arguments**:

- `name` _str_ - check name
- `descriptor` _dict_ - check descriptor
  

**Returns**:

- `Check` - check

<a name="frictionless.system.System.create_control"></a>
#### <big>create\_control</big>

```python
 | create_control(file, *, descriptor)
```

Create control

**Arguments**:

- `file` _File_ - control file
- `descriptor` _dict_ - control descriptor
  

**Returns**:

- `Control` - control

<a name="frictionless.system.System.create_dialect"></a>
#### <big>create\_dialect</big>

```python
 | create_dialect(file, *, descriptor)
```

Create dialect

**Arguments**:

- `file` _File_ - dialect file
- `descriptor` _dict_ - dialect descriptor
  

**Returns**:

- `Dialect` - dialect

<a name="frictionless.system.System.create_loader"></a>
#### <big>create\_loader</big>

```python
 | create_loader(file)
```

Create loader

**Arguments**:

- `file` _File_ - loader file
  

**Returns**:

- `Loader` - loader

<a name="frictionless.system.System.create_parser"></a>
#### <big>create\_parser</big>

```python
 | create_parser(file)
```

Create parser

**Arguments**:

- `file` _File_ - parser file
  

**Returns**:

- `Parser` - parser

<a name="frictionless.system.System.create_server"></a>
#### <big>create\_server</big>

```python
 | create_server(name)
```

Create server

**Arguments**:

- `name` _str_ - server name
  

**Returns**:

- `Server` - server

<a name="frictionless.helpers"></a>
## frictionless.helpers

<a name="frictionless.inquiry"></a>
## frictionless.inquiry

<a name="frictionless.inquiry.Inquiry"></a>
### Inquiry

```python
class Inquiry(Metadata)
```

Inquiry representation.

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.inquiry.Inquiry.tasks"></a>
#### <big>tasks</big>

```python
 | @property
 | tasks()
```

**Returns**:

- `dict[]` - tasks

<a name="frictionless.config"></a>
## frictionless.config

<a name="frictionless.header"></a>
## frictionless.header

<a name="frictionless.header.Header"></a>
### Header

```python
class Header(list)
```

Header representation

API      | Usage
-------- | --------
Public   | `from frictionless import Header`

**Arguments**:

- `cells` _any[]_ - header row cells
- `schema` _Schema_ - table schema
- `field_positions` _int[]_ - field positions

<a name="frictionless.header.Header.schema"></a>
#### <big>schema</big>

```python
 | @cached_property
 | schema()
```

**Returns**:

- `Schema` - table schema

<a name="frictionless.header.Header.field_positions"></a>
#### <big>field\_positions</big>

```python
 | @cached_property
 | field_positions()
```

**Returns**:

- `int[]` - table field positions

<a name="frictionless.header.Header.errors"></a>
#### <big>errors</big>

```python
 | @cached_property
 | errors()
```

**Returns**:

- `Error[]` - header errors

<a name="frictionless.header.Header.valid"></a>
#### <big>valid</big>

```python
 | @cached_property
 | valid()
```

**Returns**:

- `bool` - if header valid

<a name="frictionless.header.Header.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict()
```

Convert to a dict (field name -> header cell)

<a name="frictionless.header.Header.to_list"></a>
#### <big>to\_list</big>

```python
 | to_list()
```

Convert to a list

<a name="frictionless.plugins"></a>
## frictionless.plugins

<a name="frictionless.plugins.gsheet"></a>
## frictionless.plugins.gsheet

<a name="frictionless.plugins.gsheet.GsheetPlugin"></a>
### GsheetPlugin

```python
class GsheetPlugin(Plugin)
```

Plugin for Google Sheets

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheet import GsheetPlugin`

<a name="frictionless.plugins.gsheet.GsheetParser"></a>
### GsheetParser

```python
class GsheetParser(Parser)
```

Google Sheets parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheet import GsheetParser`

<a name="frictionless.plugins.gsheet.GsheetDialect"></a>
### GsheetDialect

```python
class GsheetDialect(Dialect)
```

Gsheet dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheet import GsheetDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.plugins.dataflows"></a>
## frictionless.plugins.dataflows

<a name="frictionless.plugins.dataflows.DataflowsPlugin"></a>
### DataflowsPlugin

```python
class DataflowsPlugin(Plugin)
```

Plugin for Dataflows

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.dataflows import DataflowsPlugin`

<a name="frictionless.plugins.pandas"></a>
## frictionless.plugins.pandas

<a name="frictionless.plugins.pandas.PandasPlugin"></a>
### PandasPlugin

```python
class PandasPlugin(Plugin)
```

Plugin for Pandas

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasPlugin`

<a name="frictionless.plugins.spss"></a>
## frictionless.plugins.spss

<a name="frictionless.plugins.spss.SpssPlugin"></a>
### SpssPlugin

```python
class SpssPlugin(Plugin)
```

Plugin for SPSS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssPlugin`

<a name="frictionless.plugins.elastic"></a>
## frictionless.plugins.elastic

<a name="frictionless.plugins.elastic.ElasticPlugin"></a>
### ElasticPlugin

```python
class ElasticPlugin(Plugin)
```

Plugin for ElasticSearch

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.elastic import ElasticPlugin`

<a name="frictionless.plugins.bigquery"></a>
## frictionless.plugins.bigquery

<a name="frictionless.plugins.bigquery.BigqueryPlugin"></a>
### BigqueryPlugin

```python
class BigqueryPlugin(Plugin)
```

Plugin for BigQuery

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryPlugin`

<a name="frictionless.plugins.ods"></a>
## frictionless.plugins.ods

<a name="frictionless.plugins.ods.OdsPlugin"></a>
### OdsPlugin

```python
class OdsPlugin(Plugin)
```

Plugin for ODS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsPlugin`

<a name="frictionless.plugins.ods.OdsParser"></a>
### OdsParser

```python
class OdsParser(Parser)
```

ODS parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsParser`

<a name="frictionless.plugins.ods.OdsDialect"></a>
### OdsDialect

```python
class OdsDialect(Dialect)
```

Ods dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `sheet?` _str_ - sheet
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.plugins.ods.OdsDialect.sheet"></a>
#### <big>sheet</big>

```python
 | @Metadata.property
 | sheet()
```

**Returns**:

- `int|str` - sheet

<a name="frictionless.plugins.ods.OdsDialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.plugins.html"></a>
## frictionless.plugins.html

<a name="frictionless.plugins.html.HtmlPlugin"></a>
### HtmlPlugin

```python
class HtmlPlugin(Plugin)
```

Plugin for HTML

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlPlugin`

<a name="frictionless.plugins.html.HtmlParser"></a>
### HtmlParser

```python
class HtmlParser(Parser)
```

HTML parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlParser`

<a name="frictionless.plugins.html.HtmlDialect"></a>
### HtmlDialect

```python
class HtmlDialect(Dialect)
```

Html dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `selector?` _str_ - HTML selector
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.plugins.html.HtmlDialect.selector"></a>
#### <big>selector</big>

```python
 | @Metadata.property
 | selector()
```

**Returns**:

- `str` - selector

<a name="frictionless.plugins.html.HtmlDialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.plugins.tsv"></a>
## frictionless.plugins.tsv

<a name="frictionless.plugins.tsv.TsvPlugin"></a>
### TsvPlugin

```python
class TsvPlugin(Plugin)
```

Plugin for TSV

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.tsv import TsvPlugin`

<a name="frictionless.plugins.tsv.TsvParser"></a>
### TsvParser

```python
class TsvParser(Parser)
```

TSV parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.tsv import TsvParser`

<a name="frictionless.plugins.tsv.TsvDialect"></a>
### TsvDialect

```python
class TsvDialect(Dialect)
```

Tsv dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.tsv import TsvDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.plugins.sql"></a>
## frictionless.plugins.sql

<a name="frictionless.plugins.sql.SqlPlugin"></a>
### SqlPlugin

```python
class SqlPlugin(Plugin)
```

Plugin for SQL

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlPlugin`

<a name="frictionless.plugins.sql.SqlParser"></a>
### SqlParser

```python
class SqlParser(Parser)
```

SQL parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlParser`

<a name="frictionless.plugins.sql.SqlDialect"></a>
### SqlDialect

```python
class SqlDialect(Dialect)
```

Sql dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlDialect`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `table` _str_ - table
- `order_by?` _str_ - order_by
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.plugins.ckan"></a>
## frictionless.plugins.ckan

<a name="frictionless.plugins.ckan.CkanPlugin"></a>
### CkanPlugin

```python
class CkanPlugin(Plugin)
```

Plugin for CKAN

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import CkanPlugin`

<a name="frictionless.plugins.server"></a>
## frictionless.plugins.server

<a name="frictionless.plugins.server.ServerPlugin"></a>
### ServerPlugin

```python
class ServerPlugin(Plugin)
```

Plugin for Server

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.server import ServerPlugin`

<a name="frictionless.plugins.server.ApiServer"></a>
### ApiServer

```python
class ApiServer(Server)
```

API server implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.server import ApiParser`

<a name="frictionless.plugins.aws"></a>
## frictionless.plugins.aws

<a name="frictionless.plugins.aws.AwsPlugin"></a>
### AwsPlugin

```python
class AwsPlugin(Plugin)
```

Plugin for AWS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.aws import AwsPlugin`

<a name="frictionless.plugins.aws.S3Loader"></a>
### S3Loader

```python
class S3Loader(Loader)
```

S3 loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.aws import S3Loader`

<a name="frictionless.plugins.aws.S3Control"></a>
### S3Control

```python
class S3Control(Control)
```

S3 control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.aws import S3Control`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `endpoint_url?` _string_ - endpoint url
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.plugins.aws.S3Control.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.parsers"></a>
## frictionless.parsers

<a name="frictionless.parsers.excel"></a>
## frictionless.parsers.excel

<a name="frictionless.parsers.excel.XlsxParser"></a>
### XlsxParser

```python
class XlsxParser(Parser)
```

XLSX parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import parsers`

<a name="frictionless.parsers.excel.XlsParser"></a>
### XlsParser

```python
class XlsParser(Parser)
```

XLS parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import parsers`

<a name="frictionless.parsers.csv"></a>
## frictionless.parsers.csv

<a name="frictionless.parsers.csv.CsvParser"></a>
### CsvParser

```python
class CsvParser(Parser)
```

CSV parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import parsers`

<a name="frictionless.parsers.json"></a>
## frictionless.parsers.json

<a name="frictionless.parsers.json.JsonParser"></a>
### JsonParser

```python
class JsonParser(Parser)
```

JSON parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import parser`

<a name="frictionless.parsers.json.JsonlParser"></a>
### JsonlParser

```python
class JsonlParser(Parser)
```

JSONL parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import parsers`

<a name="frictionless.parsers.inline"></a>
## frictionless.parsers.inline

<a name="frictionless.parsers.inline.InlineParser"></a>
### InlineParser

```python
class InlineParser(Parser)
```

Inline parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import parsers`

<a name="frictionless.extract"></a>
## frictionless.extract

<a name="frictionless.extract.main"></a>
## frictionless.extract.main

<a name="frictionless.extract.main.extract"></a>
#### <big>extract</big>

```python
extract(source, *, source_type=None, process=None, **options)
```

Extract resource rows into memory

API      | Usage
-------- | --------
Public   | `from frictionless import extract`

**Arguments**:

- `source` _dict|str_ - data source
- `source_type` _str_ - source type - package, resource or table
- `process?` _func_ - a row processor function
- `**options` _dict_ - options for the underlaying function
  

**Returns**:

- `Row[]|{path` - Row[]}: rows in a form depending on the source type

<a name="frictionless.extract.table"></a>
## frictionless.extract.table

<a name="frictionless.extract.table.extract_table"></a>
#### <big>extract\_table</big>

```python
extract_table(source, *, scheme=None, format=None, hashing=None, encoding=None, compression=None, compression_path=None, control=None, dialect=None, query=None, headers=None, schema=None, sync_schema=False, patch_schema=False, infer_type=None, infer_names=None, infer_volume=config.DEFAULT_INFER_VOLUME, infer_confidence=config.DEFAULT_INFER_CONFIDENCE, infer_missing_values=config.DEFAULT_MISSING_VALUES, lookup=None, process=None)
```

Extract table rows into memory

API      | Usage
-------- | --------
Public   | `from frictionless import extract_table`

**Arguments**:

  
- `source` _any_ - Source of the file; can be in various forms.
  Usually, it's a string as `<scheme>://path/to/file.<format>`.
  It also can be, for example, an array of data arrays/dictionaries.
  
- `scheme?` _str_ - Scheme for loading the file (file, http, ...).
  If not set, it'll be inferred from `source`.
  
- `format?` _str_ - File source's format (csv, xls, ...).
  If not set, it'll be inferred from `source`.
  
- `encoding?` _str_ - An algorithm to hash data.
  It defaults to 'md5'.
  
- `encoding?` _str_ - Source encoding.
  If not set, it'll be inferred from `source`.
  
- `compression?` _str_ - Source file compression (zip, ...).
  If not set, it'll be inferred from `source`.
  
- `compression_path?` _str_ - A path within the compressed file.
  It defaults to the first file in the archive.
  
- `control?` _dict|Control_ - File control.
  For more infromation, please check the Control documentation.
  
- `dialect?` _dict|Dialect_ - Table dialect.
  For more infromation, please check the Dialect documentation.
  
- `query?` _dict|Query_ - Table query.
  For more infromation, please check the Query documentation.
  
- `headers?` _int|int[]|[int[], str]_ - Either a row
  number or list of row numbers (in case of multi-line headers) to be
  considered as headers (rows start counting at 1), or a pair
  where the first element is header rows and the second the
  header joiner.  It defaults to 1.
  
- `schema?` _dict|Schema_ - Table schema.
  For more infromation, please check the Schema documentation.
  
- `sync_schema?` _bool_ - Whether to sync the schema.
  If it sets to `True` the provided schema will be mapped to
  the inferred schema. It means that, for example, you can
  provide a subset of fileds to be applied on top of the inferred
  fields or the provided schema can have different order of fields.
  
- `patch_schema?` _dict_ - A dictionary to be used as an inferred schema patch.
  The form of this dictionary should follow the Schema descriptor form
  except for the `fields` property which should be a mapping with the
  key named after a field name and the values being a field patch.
  For more information, please check "Extracting Data" guide.
  
- `infer_type?` _str_ - Enforce all the inferred types to be this type.
  For more information, please check "Describing  Data" guide.
  
- `infer_names?` _str[]_ - Enforce all the inferred fields to have provided names.
  For more information, please check "Describing  Data" guide.
  
- `infer_volume?` _int_ - The amount of rows to be extracted as a samle.
  For more information, please check "Describing  Data" guide.
  It defaults to 100
  
- `infer_confidence?` _float_ - A number from 0 to 1 setting the infer confidence.
  If  1 the data is guaranteed to be valid against the inferred schema.
  For more information, please check "Describing  Data" guide.
  It defaults to 0.9
  
- `infer_missing_values?` _str[]_ - String to be considered as missing values.
  For more information, please check "Describing  Data" guide.
  It defaults to `['']`
  
- `lookup?` _dict_ - The lookup is a special object providing relational information.
  For more information, please check "Extracting  Data" guide.
  
- `process?` _func_ - a row processor function
  

**Returns**:

- `Row[]` - an array for rows

<a name="frictionless.extract.package"></a>
## frictionless.extract.package

<a name="frictionless.extract.package.extract_package"></a>
#### <big>extract\_package</big>

```python
extract_package(source, *, process=None)
```

Extract package rows into memory

API      | Usage
-------- | --------
Public   | `from frictionless import extract_package`

**Arguments**:

- `source` _dict|str_ - data resource descriptor
- `process?` _func_ - a row processor function
  

**Returns**:

- `{path` - Row[]}: a dictionary of arrays of rows

<a name="frictionless.extract.resource"></a>
## frictionless.extract.resource

<a name="frictionless.extract.resource.extract_resource"></a>
#### <big>extract\_resource</big>

```python
extract_resource(source, *, process=None)
```

Extract resource rows into memory

API      | Usage
-------- | --------
Public   | `from frictionless import extract_resource`

**Arguments**:

- `source` _dict|str_ - data resource descriptor
- `process?` _func_ - a row processor function
  

**Returns**:

- `Row[]` - an array of rows

<a name="frictionless.errors"></a>
## frictionless.errors

<a name="frictionless.errors.Error"></a>
### Error

```python
class Error(Metadata)
```

Error representation

API      | Usage
-------- | --------
Public   | `from frictionless import errors`

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.errors.Error.note"></a>
#### <big>note</big>

```python
 | @property
 | note()
```

**Returns**:

- `str` - note

<a name="frictionless.errors.Error.message"></a>
#### <big>message</big>

```python
 | @property
 | message()
```

**Returns**:

- `str` - message

<a name="frictionless.errors.HeaderError"></a>
### HeaderError

```python
class HeaderError(Error)
```

Header error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `cells` _str[]_ - header cells
- `cell` _str_ - an errored cell
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.errors.RowError"></a>
### RowError

```python
class RowError(Error)
```

Row error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `row_number` _int_ - row number
- `row_position` _int_ - row position
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.errors.RowError.from_row"></a>
#### <big>from\_row</big>

```python
 | @classmethod
 | from_row(cls, row, *, note)
```

Create an error from a row

**Arguments**:

- `row` _Row_ - row
- `note` _str_ - note
  

**Returns**:

- `RowError` - error

<a name="frictionless.errors.CellError"></a>
### CellError

```python
class CellError(RowError)
```

Cell error representation

**Arguments**:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `cells` _str[]_ - row cells
- `row_number` _int_ - row number
- `row_position` _int_ - row position
- `cell` _str_ - errored cell
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  
  # Raises
- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.errors.CellError.from_row"></a>
#### <big>from\_row</big>

```python
 | @classmethod
 | from_row(cls, row, *, note, field_name)
```

Create and error from a cell

**Arguments**:

- `row` _Row_ - row
- `note` _str_ - note
- `field_name` _str_ - field name
  

**Returns**:

- `CellError` - error

<a name="frictionless.describe"></a>
## frictionless.describe

<a name="frictionless.describe.main"></a>
## frictionless.describe.main

<a name="frictionless.describe.main.describe"></a>
#### <big>describe</big>

```python
describe(source, *, source_type=None, **options)
```

Describe the data source

API      | Usage
-------- | --------
Public   | `from frictionless import describe`

**Arguments**:

- `source` _any_ - data source
- `source_type` _str_ - source type - `schema`, `resource` or `package`
- `**options` _dict_ - options for the underlaying describe function
  

**Returns**:

- `Package|Resource|Schema` - metadata

<a name="frictionless.describe.package"></a>
## frictionless.describe.package

<a name="frictionless.describe.package.describe_package"></a>
#### <big>describe\_package</big>

```python
describe_package(source, *, expand=False)
```

Describe the given source as a package

API      | Usage
-------- | --------
Public   | `from frictionless import describe_package`

**Arguments**:

- `source` _any_ - data source
- `expand?` _bool_ - if `True` it will expand the metadata
  

**Returns**:

- `Package` - data package

<a name="frictionless.describe.schema"></a>
## frictionless.describe.schema

<a name="frictionless.describe.schema.describe_schema"></a>
#### <big>describe\_schema</big>

```python
describe_schema(source, **options)
```

Describe schema of the given source

API      | Usage
-------- | --------
Public   | `from frictionless import describe_schema`

**Arguments**:

- `source` _any_ - data source
- `**options` _dict_ - see `describe_resource` options
  

**Returns**:

- `Schema` - table schema

<a name="frictionless.describe.resource"></a>
## frictionless.describe.resource

<a name="frictionless.describe.resource.describe_resource"></a>
#### <big>describe\_resource</big>

```python
describe_resource(source, *, scheme=None, format=None, hashing=None, encoding=None, compression=None, compression_path=None, control=None, dialect=None, query=None, headers=None, infer_type=None, infer_names=None, infer_volume=config.DEFAULT_INFER_VOLUME, infer_confidence=config.DEFAULT_INFER_CONFIDENCE, infer_missing_values=config.DEFAULT_MISSING_VALUES, expand=False)
```

Describe the given source as a resource

API      | Usage
-------- | --------
Public   | `from frictionless import describe_resource`

**Arguments**:

  
- `source` _any_ - Source of the file; can be in various forms.
  Usually, it's a string as `<scheme>://path/to/file.<format>`.
  It also can be, for example, an array of data arrays/dictionaries.
  
- `scheme?` _str_ - Scheme for loading the file (file, http, ...).
  If not set, it'll be inferred from `source`.
  
- `format?` _str_ - File source's format (csv, xls, ...).
  If not set, it'll be inferred from `source`.
  
- `encoding?` _str_ - An algorithm to hash data.
  It defaults to 'md5'.
  
- `encoding?` _str_ - Source encoding.
  If not set, it'll be inferred from `source`.
  
- `compression?` _str_ - Source file compression (zip, ...).
  If not set, it'll be inferred from `source`.
  
- `compression_path?` _str_ - A path within the compressed file.
  It defaults to the first file in the archive.
  
- `control?` _dict|Control_ - File control.
  For more infromation, please check the Control documentation.
  
- `dialect?` _dict|Dialect_ - Table dialect.
  For more infromation, please check the Dialect documentation.
  
- `query?` _dict|Query_ - Table query.
  For more infromation, please check the Query documentation.
  
- `headers?` _int|int[]|[int[], str]_ - Either a row
  number or list of row numbers (in case of multi-line headers) to be
  considered as headers (rows start counting at 1), or a pair
  where the first element is header rows and the second the
  header joiner.  It defaults to 1.
  
- `infer_type?` _str_ - Enforce all the inferred types to be this type.
  For more information, please check "Describing  Data" guide.
  
- `infer_names?` _str[]_ - Enforce all the inferred fields to have provided names.
  For more information, please check "Describing  Data" guide.
  
- `infer_volume?` _int_ - The amount of rows to be extracted as a samle.
  For more information, please check "Describing  Data" guide.
  It defaults to 100
  
- `infer_confidence?` _float_ - A number from 0 to 1 setting the infer confidence.
  If  1 the data is guaranteed to be valid against the inferred schema.
  For more information, please check "Describing  Data" guide.
  It defaults to 0.9
  
- `infer_missing_values?` _str[]_ - String to be considered as missing values.
  For more information, please check "Describing  Data" guide.
  It defaults to `['']`
  
- `expand?` _bool_ - if `True` it will expand the metadata
  

**Returns**:

- `Resource` - data resource

<a name="frictionless.schema"></a>
## frictionless.schema

<a name="frictionless.schema.Schema"></a>
### Schema

```python
class Schema(Metadata)
```

Schema representation

API      | Usage
-------- | --------
Public   | `from frictionless import Schema`

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
- `fields?` _dict[]_ - list of field descriptors
- `missing_values?` _str[]_ - missing values
- `primary_key?` _str[]_ - primary key
- `foreign_keys?` _dict[]_ - foreign keys
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.schema.Schema.missing_values"></a>
#### <big>missing\_values</big>

```python
 | @Metadata.property
 | missing_values()
```

**Returns**:

- `str[]` - missing values

<a name="frictionless.schema.Schema.primary_key"></a>
#### <big>primary\_key</big>

```python
 | @Metadata.property
 | primary_key()
```

**Returns**:

- `str[]` - primary key field names

<a name="frictionless.schema.Schema.foreign_keys"></a>
#### <big>foreign\_keys</big>

```python
 | @Metadata.property
 | foreign_keys()
```

**Returns**:

- `dict[]` - foreign keys

<a name="frictionless.schema.Schema.fields"></a>
#### <big>fields</big>

```python
 | @Metadata.property
 | fields()
```

**Returns**:

- `Field[]` - an array of field instances

<a name="frictionless.schema.Schema.field_names"></a>
#### <big>field\_names</big>

```python
 | @Metadata.property(write=False)
 | field_names()
```

**Returns**:

- `str[]` - an array of field names

<a name="frictionless.schema.Schema.add_field"></a>
#### <big>add\_field</big>

```python
 | add_field(descriptor)
```

Add new field to schema.

The schema descriptor will be validated with newly added field descriptor.

**Arguments**:

- `descriptor` _dict_ - field descriptor
  

**Returns**:

- `Field/None` - added `Field` instance or `None` if not added

<a name="frictionless.schema.Schema.get_field"></a>
#### <big>get\_field</big>

```python
 | get_field(name)
```

Get schema's field by name.

**Arguments**:

- `name` _str_ - schema field name
  

**Returns**:

- `Field/None` - `Field` instance or `None` if not found

<a name="frictionless.schema.Schema.has_field"></a>
#### <big>has\_field</big>

```python
 | has_field(name)
```

Check if a field is present

**Arguments**:

- `name` _str_ - schema field name
  

**Returns**:

- `bool` - whether there is the field

<a name="frictionless.schema.Schema.remove_field"></a>
#### <big>remove\_field</big>

```python
 | remove_field(name)
```

Remove field by name.

The schema descriptor will be validated after field descriptor removal.

**Arguments**:

- `name` _str_ - schema field name
  

**Returns**:

- `Field/None` - removed `Field` instances or `None` if not found

<a name="frictionless.schema.Schema.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand the schema

<a name="frictionless.schema.Schema.infer"></a>
#### <big>infer</big>

```python
 | infer(sample, *, type=None, names=None, confidence=config.DEFAULT_INFER_CONFIDENCE, missing_values=config.DEFAULT_MISSING_VALUES)
```

Infer schema

**Arguments**:

- `sample` _any[][]_ - data sample
- `type?` _str_ - enforce all the field to be the given type
- `names` _str[]_ - enforce field names
- `confidence` _float_ - infer confidence from 0 to 1
- `missing_values` _str[]_ - provide custom missing values

<a name="frictionless.schema.Schema.read_data"></a>
#### <big>read\_data</big>

```python
 | read_data(cells)
```

Read a list of cells (normalize/cast)

**Arguments**:

- `cells` _any[]_ - list of cells
  

**Returns**:

- `any[]` - list of processed cells

<a name="frictionless.schema.Schema.write_data"></a>
#### <big>write\_data</big>

```python
 | write_data(cells, *, native_types=[])
```

Write a list of cells (normalize/uncast)

**Arguments**:

- `cells` _any[]_ - list of cells
  

**Returns**:

- `any[]` - list of processed cells

<a name="frictionless.schema.Schema.from_sample"></a>
#### <big>from\_sample</big>

```python
 | @staticmethod
 | from_sample(sample, *, type=None, names=None, confidence=config.DEFAULT_INFER_CONFIDENCE, missing_values=config.DEFAULT_MISSING_VALUES)
```

Infer schema from sample

**Arguments**:

- `sample` _any[][]_ - data sample
- `type?` _str_ - enforce all the field to be the given type
- `names` _str[]_ - enforce field names
- `confidence` _float_ - infer confidence from 0 to 1
- `missing_values` _str[]_ - provide custom missing values
  

**Returns**:

- `Schema` - schema

<a name="frictionless.schema.Schema.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert resource to dict

**Arguments**:

- `expand` _bool_ - whether to expand

<a name="frictionless.check"></a>
## frictionless.check

<a name="frictionless.check.Check"></a>
### Check

```python
class Check(Metadata)
```

Check representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Checks`

It's an interface for writing Frictionless checks.

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
  

**Raises**:

- `FrictionlessException` - raise if metadata is invalid

<a name="frictionless.check.Check.table"></a>
#### <big>table</big>

```python
 | @property
 | table()
```

**Returns**:

- `Table?` - table object available after the `check.connect` call

<a name="frictionless.check.Check.connect"></a>
#### <big>connect</big>

```python
 | connect(table)
```

Connect to the given table

**Arguments**:

- `table` _Table_ - data table

<a name="frictionless.check.Check.prepare"></a>
#### <big>prepare</big>

```python
 | prepare()
```

Called before validation

<a name="frictionless.check.Check.validate_task"></a>
#### <big>validate\_task</big>

```python
 | validate_task()
```

Called to validate the check itself

**Yields**:

- `Error` - found errors

<a name="frictionless.check.Check.validate_schema"></a>
#### <big>validate\_schema</big>

```python
 | validate_schema(schema)
```

Called to validate the given schema

**Arguments**:

- `schema` _Schema_ - table schema
  

**Yields**:

- `Error` - found errors

<a name="frictionless.check.Check.validate_header"></a>
#### <big>validate\_header</big>

```python
 | validate_header(header)
```

Called to validate the given header

**Arguments**:

- `header` _Header_ - table header
  

**Yields**:

- `Error` - found errors

<a name="frictionless.check.Check.validate_row"></a>
#### <big>validate\_row</big>

```python
 | validate_row(row)
```

Called to validate the given row (on every row)

**Arguments**:

- `row` _Row_ - table row
  

**Yields**:

- `Error` - found errors

<a name="frictionless.check.Check.validate_table"></a>
#### <big>validate\_table</big>

```python
 | validate_table()
```

Called to validate the table (after no rows left)

**Yields**:

- `Error` - found errors

<a name="frictionless.resource"></a>
## frictionless.resource

<a name="frictionless.resource.Resource"></a>
### Resource

```python
class Resource(Metadata)
```

Resource representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Resource`

**Arguments**:

- `descriptor?` _str|dict_ - report descriptor
- `name?` _str_ - package name (for machines)
- `title?` _str_ - package title (for humans)
- `descriptor?` _str_ - package descriptor
- `path?` _str_ - file path
- `data?` _any[][]_ - array or data arrays
- `scheme?` _str_ - file scheme
- `format?` _str_ - file format
- `hashing?` _str_ - file hashing
- `encoding?` _str_ - file encoding
- `compression?` _str_ - file compression
- `compression_path?` _str_ - file compression path
- `dialect?` _dict_ - table dialect
- `schema?` _dict_ - file schema
- `profile?` _str_ - resource profile
- `basepath?` _str_ - resource basepath
- `trusted?` _bool_ - don't raise on unsage paths
- `package?` _Package_ - resource package
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.resource.Resource.name"></a>
#### <big>name</big>

```python
 | @Metadata.property
 | name()
```

Returns
    str: resource name

<a name="frictionless.resource.Resource.title"></a>
#### <big>title</big>

```python
 | @Metadata.property
 | title()
```

Returns
    str: resource title

<a name="frictionless.resource.Resource.description"></a>
#### <big>description</big>

```python
 | @Metadata.property
 | description()
```

Returns
    str: resource description

<a name="frictionless.resource.Resource.path"></a>
#### <big>path</big>

```python
 | @Metadata.property
 | path()
```

Returns
    str?: resource path

<a name="frictionless.resource.Resource.data"></a>
#### <big>data</big>

```python
 | @Metadata.property
 | data()
```

Returns
    any[][]?: resource data

<a name="frictionless.resource.Resource.source"></a>
#### <big>source</big>

```python
 | @Metadata.property(write=False)
 | source()
```

Returns
    any: data source

<a name="frictionless.resource.Resource.basepath"></a>
#### <big>basepath</big>

```python
 | @Metadata.property(write=False)
 | basepath()
```

Returns
    str: resource basepath

<a name="frictionless.resource.Resource.fullpath"></a>
#### <big>fullpath</big>

```python
 | @Metadata.property(write=False)
 | fullpath()
```

Returns
    str: resource fullpath

<a name="frictionless.resource.Resource.inline"></a>
#### <big>inline</big>

```python
 | @Metadata.property(write=False)
 | inline()
```

Returns
    bool: if resource is inline

<a name="frictionless.resource.Resource.tabular"></a>
#### <big>tabular</big>

```python
 | @Metadata.property(write=False)
 | tabular()
```

Returns
    bool: if resource is tabular

<a name="frictionless.resource.Resource.remote"></a>
#### <big>remote</big>

```python
 | @Metadata.property(write=False)
 | remote()
```

Returns
    bool: if resource is remote

<a name="frictionless.resource.Resource.multipart"></a>
#### <big>multipart</big>

```python
 | @Metadata.property(write=False)
 | multipart()
```

Returns
    bool: if resource is multipart

<a name="frictionless.resource.Resource.scheme"></a>
#### <big>scheme</big>

```python
 | @Metadata.property
 | scheme()
```

Returns
    str?: resource scheme

<a name="frictionless.resource.Resource.format"></a>
#### <big>format</big>

```python
 | @Metadata.property
 | format()
```

Returns
    str?: resource format

<a name="frictionless.resource.Resource.hashing"></a>
#### <big>hashing</big>

```python
 | @Metadata.property
 | hashing()
```

Returns
    str?: resource hashing

<a name="frictionless.resource.Resource.encoding"></a>
#### <big>encoding</big>

```python
 | @Metadata.property
 | encoding()
```

Returns
    str?: resource encoding

<a name="frictionless.resource.Resource.compression"></a>
#### <big>compression</big>

```python
 | @Metadata.property
 | compression()
```

Returns
    str?: resource compression

<a name="frictionless.resource.Resource.compression_path"></a>
#### <big>compression\_path</big>

```python
 | @Metadata.property
 | compression_path()
```

Returns
    str?: resource compression path

<a name="frictionless.resource.Resource.stats"></a>
#### <big>stats</big>

```python
 | @Metadata.property
 | stats()
```

Returns
    dict?: resource stats

<a name="frictionless.resource.Resource.dialect"></a>
#### <big>dialect</big>

```python
 | @Metadata.property
 | dialect()
```

Returns
    Dialect?: resource dialect

<a name="frictionless.resource.Resource.schema"></a>
#### <big>schema</big>

```python
 | @Metadata.property
 | schema()
```

Returns
    Schema: resource schema

<a name="frictionless.resource.Resource.profile"></a>
#### <big>profile</big>

```python
 | @Metadata.property
 | profile()
```

Returns
    str?: resource profile

<a name="frictionless.resource.Resource.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.resource.Resource.infer"></a>
#### <big>infer</big>

```python
 | infer(source=None, *, only_sample=False)
```

Infer metadata

**Arguments**:

- `source` _str|str[]_ - path, list of paths or glob pattern
- `only_sample?` _bool_ - infer whatever possible but only from the sample

<a name="frictionless.resource.Resource.read_bytes"></a>
#### <big>read\_bytes</big>

```python
 | read_bytes()
```

**Returns**:

- `bytes` - resource bytes

<a name="frictionless.resource.Resource.read_byte_stream"></a>
#### <big>read\_byte\_stream</big>

```python
 | read_byte_stream()
```

**Returns**:

- `io.ByteStream` - resource byte stream

<a name="frictionless.resource.Resource.read_text"></a>
#### <big>read\_text</big>

```python
 | read_text()
```

**Returns**:

- `str` - resource text

<a name="frictionless.resource.Resource.read_text_stream"></a>
#### <big>read\_text\_stream</big>

```python
 | read_text_stream()
```

**Returns**:

- `io.TextStream` - resource text stream

<a name="frictionless.resource.Resource.read_data"></a>
#### <big>read\_data</big>

```python
 | read_data()
```

**Returns**:

- `any[][]` - array of data arrays

<a name="frictionless.resource.Resource.read_data_stream"></a>
#### <big>read\_data\_stream</big>

```python
 | read_data_stream()
```

**Returns**:

- `gen<any[][]>` - data stream

<a name="frictionless.resource.Resource.read_rows"></a>
#### <big>read\_rows</big>

```python
 | read_rows()
```

Returns
    Row[]: resource rows

<a name="frictionless.resource.Resource.read_row_stream"></a>
#### <big>read\_row\_stream</big>

```python
 | read_row_stream()
```

Returns
    gen<Row[]>: row stream

<a name="frictionless.resource.Resource.read_header"></a>
#### <big>read\_header</big>

```python
 | read_header()
```

Returns
    Header: resource header

<a name="frictionless.resource.Resource.read_sample"></a>
#### <big>read\_sample</big>

```python
 | read_sample()
```

Returns
    any[][]: resource sample

<a name="frictionless.resource.Resource.read_stats"></a>
#### <big>read\_stats</big>

```python
 | read_stats()
```

Returns
    dict: resource stats

<a name="frictionless.resource.Resource.read_lookup"></a>
#### <big>read\_lookup</big>

```python
 | read_lookup()
```

Returns
    dict: resource lookup structure

<a name="frictionless.resource.Resource.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert resource to dict

**Arguments**:

- `expand` _bool_ - whether to expand

<a name="frictionless.resource.Resource.to_table"></a>
#### <big>to\_table</big>

```python
 | to_table(**options)
```

Convert resource to Table

**Arguments**:

- `**options` _dict_ - table options
  

**Returns**:

- `Table` - data table

<a name="frictionless.resource.Resource.to_file"></a>
#### <big>to\_file</big>

```python
 | to_file(**options)
```

Convert resource to File

**Arguments**:

- `**options` _dict_ - file options
  

**Returns**:

- `File` - data file

<a name="frictionless.resource.Resource.to_zip"></a>
#### <big>to\_zip</big>

```python
 | to_zip(target)
```

Save resource to a zip

**Arguments**:

- `target` _str_ - target path
  

**Raises**:

- `FrictionlessException` - on any error

<a name="frictionless.exceptions"></a>
## frictionless.exceptions

<a name="frictionless.exceptions.FrictionlessException"></a>
### FrictionlessException

```python
class FrictionlessException(Exception)
```

Main Frictionless exception

API      | Usage
-------- | --------
Public   | `from frictionless import exceptions`

**Arguments**:

- `error` _Error_ - an underlaying error

<a name="frictionless.exceptions.FrictionlessException.error"></a>
#### <big>error</big>

```python
 | @property
 | error()
```

**Returns**:

- `Error` - error

<a name="frictionless.transform"></a>
## frictionless.transform

<a name="frictionless.transform.main"></a>
## frictionless.transform.main

<a name="frictionless.transform.main.transform"></a>
#### <big>transform</big>

```python
transform(source)
```

Transform resource

API      | Usage
-------- | --------
Public   | `from frictionless import transform`

**Arguments**:

- `source` _any_ - data source

<a name="frictionless.transform.package"></a>
## frictionless.transform.package

<a name="frictionless.transform.package.transform_package"></a>
#### <big>transform\_package</big>

```python
transform_package(source)
```

Transform package

API      | Usage
-------- | --------
Public   | `from frictionless import transform_package`

**Arguments**:

- `source` _any_ - a pipeline descriptor

<a name="frictionless.transform.resource"></a>
## frictionless.transform.resource

<a name="frictionless.transform.resource.transform_resource"></a>
#### <big>transform\_resource</big>

```python
transform_resource(source)
```

Transform resource

API      | Usage
-------- | --------
Public   | `from frictionless import transform_resource`

**Arguments**:

- `source` _any_ - data source

<a name="frictionless.parser"></a>
## frictionless.parser

<a name="frictionless.parser.Parser"></a>
### Parser

```python
class Parser()
```

Parser representation

API      | Usage
-------- | --------
Public   | `from frictionless import Parser`

**Arguments**:

- `file` _File_ - file

<a name="frictionless.parser.Parser.file"></a>
#### <big>file</big>

```python
 | @property
 | file()
```

**Returns**:

- `File` - file

<a name="frictionless.parser.Parser.loader"></a>
#### <big>loader</big>

```python
 | @property
 | loader()
```

**Returns**:

- `Loader` - loader

<a name="frictionless.parser.Parser.data_stream"></a>
#### <big>data\_stream</big>

```python
 | @property
 | data_stream()
```

**Yields**:

- `any[][]` - data stream

<a name="frictionless.parser.Parser.open"></a>
#### <big>open</big>

```python
 | open()
```

Open the parser as "io.open" does

<a name="frictionless.parser.Parser.close"></a>
#### <big>close</big>

```python
 | close()
```

Close the parser as "filelike.close" does

<a name="frictionless.parser.Parser.closed"></a>
#### <big>closed</big>

```python
 | @property
 | closed()
```

Whether the parser is closed

**Returns**:

- `bool` - if closed

<a name="frictionless.parser.Parser.read_loader"></a>
#### <big>read\_loader</big>

```python
 | read_loader()
```

Create and open loader

**Returns**:

- `Loader` - loader

<a name="frictionless.parser.Parser.read_data_stream"></a>
#### <big>read\_data\_stream</big>

```python
 | read_data_stream()
```

Read data stream

**Returns**:

- `gen<any[][]>` - data stream

<a name="frictionless.parser.Parser.read_data_stream_create"></a>
#### <big>read\_data\_stream\_create</big>

```python
 | read_data_stream_create(loader)
```

Create data stream from loader

**Arguments**:

- `loader` _Loader_ - loader
  

**Returns**:

- `gen<any[][]>` - data stream

<a name="frictionless.parser.Parser.read_data_stream_handle_errors"></a>
#### <big>read\_data\_stream\_handle\_errors</big>

```python
 | read_data_stream_handle_errors(data_stream)
```

Wrap data stream into error handler

**Arguments**:

- `gen<any[][]>` - data stream
  

**Returns**:

- `gen<any[][]>` - data stream

<a name="frictionless.parser.Parser.write"></a>
#### <big>write</big>

```python
 | write(row_stream)
```

Write row stream into the file

**Arguments**:

- `gen<Row[]>` - row stream

<a name="frictionless.report"></a>
## frictionless.report

<a name="frictionless.report.Report"></a>
### Report

```python
class Report(Metadata)
```

Report representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Report`

**Arguments**:

- `descriptor?` _str|dict_ - report descriptor
- `time` _float_ - validation time
- `errors` _Error[]_ - validation errors
- `tables` _ReportTable[]_ - validation tables
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.report.Report.version"></a>
#### <big>version</big>

```python
 | @property
 | version()
```

**Returns**:

- `str` - frictionless version

<a name="frictionless.report.Report.time"></a>
#### <big>time</big>

```python
 | @property
 | time()
```

**Returns**:

- `float` - validation time

<a name="frictionless.report.Report.valid"></a>
#### <big>valid</big>

```python
 | @property
 | valid()
```

**Returns**:

- `bool` - validation result

<a name="frictionless.report.Report.stats"></a>
#### <big>stats</big>

```python
 | @property
 | stats()
```

**Returns**:

- `dict` - validation stats

<a name="frictionless.report.Report.errors"></a>
#### <big>errors</big>

```python
 | @property
 | errors()
```

**Returns**:

- `Error[]` - validation errors

<a name="frictionless.report.Report.tables"></a>
#### <big>tables</big>

```python
 | @property
 | tables()
```

**Returns**:

- `ReportTable[]` - validation tables

<a name="frictionless.report.Report.table"></a>
#### <big>table</big>

```python
 | @property
 | table()
```

**Returns**:

- `ReportTable` - validation table (if there is only one)
  

**Raises**:

- `FrictionlessException` - if there are more that 1 table

<a name="frictionless.report.Report.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.report.Report.flatten"></a>
#### <big>flatten</big>

```python
 | flatten(spec)
```

Flatten the report

Parameters
spec (any[]): flatten specification

**Returns**:

- `any[]` - flatten report

<a name="frictionless.report.Report.from_validate"></a>
#### <big>from\_validate</big>

```python
 | @staticmethod
 | from_validate(validate)
```

Validate function wrapper

**Arguments**:

- `validate` _func_ - validate
  

**Returns**:

- `func` - wrapped validate

<a name="frictionless.report.Report.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert field to dict

**Arguments**:

- `expand` _bool_ - whether to expand

<a name="frictionless.report.ReportTable"></a>
### ReportTable

```python
class ReportTable(Metadata)
```

Report table representation.

API      | Usage
-------- | --------
Public   | `from frictionless import ReportTable`

**Arguments**:

- `descriptor?` _str|dict_ - schema descriptor
- `time` _float_ - validation time
- `scope` _str[]_ - validation scope
- `partial` _bool_ - wehter validation was partial
- `errors` _Error[]_ - validation errors
- `table` _Table_ - validation table
  
  # Raises
- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.report.ReportTable.path"></a>
#### <big>path</big>

```python
 | @property
 | path()
```

**Returns**:

- `str` - path

<a name="frictionless.report.ReportTable.scheme"></a>
#### <big>scheme</big>

```python
 | @property
 | scheme()
```

**Returns**:

- `str` - scheme

<a name="frictionless.report.ReportTable.format"></a>
#### <big>format</big>

```python
 | @property
 | format()
```

**Returns**:

- `str` - format

<a name="frictionless.report.ReportTable.hashing"></a>
#### <big>hashing</big>

```python
 | @property
 | hashing()
```

**Returns**:

- `str` - hashing

<a name="frictionless.report.ReportTable.encoding"></a>
#### <big>encoding</big>

```python
 | @property
 | encoding()
```

**Returns**:

- `str` - encoding

<a name="frictionless.report.ReportTable.compression"></a>
#### <big>compression</big>

```python
 | @property
 | compression()
```

**Returns**:

- `str` - compression

<a name="frictionless.report.ReportTable.compression_path"></a>
#### <big>compression\_path</big>

```python
 | @property
 | compression_path()
```

**Returns**:

- `str` - compression path

<a name="frictionless.report.ReportTable.dialect"></a>
#### <big>dialect</big>

```python
 | @property
 | dialect()
```

**Returns**:

- `Dialect` - dialect

<a name="frictionless.report.ReportTable.query"></a>
#### <big>query</big>

```python
 | @property
 | query()
```

**Returns**:

- `Query` - query

<a name="frictionless.report.ReportTable.header"></a>
#### <big>header</big>

```python
 | @property
 | header()
```

**Returns**:

- `Header` - header

<a name="frictionless.report.ReportTable.schema"></a>
#### <big>schema</big>

```python
 | @property
 | schema()
```

**Returns**:

- `Schema` - schema

<a name="frictionless.report.ReportTable.time"></a>
#### <big>time</big>

```python
 | @property
 | time()
```

**Returns**:

- `float` - validation time

<a name="frictionless.report.ReportTable.valid"></a>
#### <big>valid</big>

```python
 | @property
 | valid()
```

**Returns**:

- `bool` - validation result

<a name="frictionless.report.ReportTable.scope"></a>
#### <big>scope</big>

```python
 | @property
 | scope()
```

**Returns**:

- `str[]` - validation scope

<a name="frictionless.report.ReportTable.stats"></a>
#### <big>stats</big>

```python
 | @property
 | stats()
```

**Returns**:

- `dict` - validation stats

<a name="frictionless.report.ReportTable.partial"></a>
#### <big>partial</big>

```python
 | @property
 | partial()
```

**Returns**:

- `bool` - if validation partial

<a name="frictionless.report.ReportTable.errors"></a>
#### <big>errors</big>

```python
 | @property
 | errors()
```

**Returns**:

- `Error[]` - validation errors

<a name="frictionless.report.ReportTable.error"></a>
#### <big>error</big>

```python
 | @property
 | error()
```

**Returns**:

- `Error` - validation error if there is only one
  

**Raises**:

- `FrictionlessException` - if more than one errors

<a name="frictionless.report.ReportTable.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.report.ReportTable.flatten"></a>
#### <big>flatten</big>

```python
 | flatten(spec)
```

Flatten the report

Parameters
spec (any[]): flatten specification

**Returns**:

- `any[]` - flatten table report

<a name="frictionless.report.ReportTable.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Convert field to dict

**Arguments**:

- `expand` _bool_ - whether to expand

<a name="frictionless.dialects"></a>
## frictionless.dialects

<a name="frictionless.dialects.Dialect"></a>
### Dialect

```python
class Dialect(Metadata)
```

Dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless import dialects`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `header?` _bool_ - whether there is a header row
- `headerRows?` _int[]_ - row numbers of header rows
- `headerJoin?` _str_ - a multiline header joiner
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.dialects.Dialect.header"></a>
#### <big>header</big>

```python
 | @Metadata.property
 | header()
```

**Returns**:

- `bool` - if there is a header row

<a name="frictionless.dialects.Dialect.header_rows"></a>
#### <big>header\_rows</big>

```python
 | @Metadata.property
 | header_rows()
```

**Returns**:

- `int[]` - header rows

<a name="frictionless.dialects.Dialect.header_join"></a>
#### <big>header\_join</big>

```python
 | @Metadata.property
 | header_join()
```

**Returns**:

- `str` - header joiner

<a name="frictionless.dialects.Dialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.dialects.Dialect.to_dict"></a>
#### <big>to\_dict</big>

```python
 | to_dict(expand=False)
```

Conver to a dict

**Arguments**:

- `expand` _bool_ - if True call `metadata.expand` for the exported copy

<a name="frictionless.dialects.CsvDialect"></a>
### CsvDialect

```python
class CsvDialect(Dialect)
```

Csv dialect representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `delimiter?` _str_ - csv delimiter
- `line_terminator?` _str_ - csv line terminator
- `quote_char?` _str_ - csv quote char
- `double_quote?` _bool_ - csv double quote
- `escape_char?` _str_ - csv escape char
- `null_sequence?` _str_ - csv null sequence
- `skip_initial_space?` _bool_ - csv skip initial space
- `comment_char?` _str_ - csv comment char
- `case_sensitive_header?` _bool_ - csv case sensitive header
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.dialects.CsvDialect.delimiter"></a>
#### <big>delimiter</big>

```python
 | @Metadata.property
 | delimiter()
```

**Returns**:

- `str` - delimiter

<a name="frictionless.dialects.CsvDialect.line_terminator"></a>
#### <big>line\_terminator</big>

```python
 | @Metadata.property
 | line_terminator()
```

**Returns**:

- `str` - line terminator

<a name="frictionless.dialects.CsvDialect.quote_char"></a>
#### <big>quote\_char</big>

```python
 | @Metadata.property
 | quote_char()
```

**Returns**:

- `str` - quote char

<a name="frictionless.dialects.CsvDialect.double_quote"></a>
#### <big>double\_quote</big>

```python
 | @Metadata.property
 | double_quote()
```

**Returns**:

- `bool` - double quote

<a name="frictionless.dialects.CsvDialect.escape_char"></a>
#### <big>escape\_char</big>

```python
 | @Metadata.property
 | escape_char()
```

**Returns**:

- `str?` - escape char

<a name="frictionless.dialects.CsvDialect.null_sequence"></a>
#### <big>null\_sequence</big>

```python
 | @Metadata.property
 | null_sequence()
```

**Returns**:

- `str?` - null sequence

<a name="frictionless.dialects.CsvDialect.skip_initial_space"></a>
#### <big>skip\_initial\_space</big>

```python
 | @Metadata.property
 | skip_initial_space()
```

**Returns**:

- `bool` - if skipping initial space

<a name="frictionless.dialects.CsvDialect.comment_char"></a>
#### <big>comment\_char</big>

```python
 | @Metadata.property
 | comment_char()
```

**Returns**:

- `str?` - comment char

<a name="frictionless.dialects.CsvDialect.case_sensitive_header"></a>
#### <big>case\_sensitive\_header</big>

```python
 | @Metadata.property
 | case_sensitive_header()
```

**Returns**:

- `bool` - case sensitive header

<a name="frictionless.dialects.CsvDialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.dialects.CsvDialect.to_python"></a>
#### <big>to\_python</big>

```python
 | to_python()
```

Conver to Python's `csv.Dialect`

<a name="frictionless.dialects.ExcelDialect"></a>
### ExcelDialect

```python
class ExcelDialect(Dialect)
```

Excel dialect representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `sheet?` _int|str_ - number from 1 or name of an excel sheet
- `workbook_cache?` _dict_ - workbook cache
- `fill_merged_cells?` _bool_ - whether to fill merged cells
- `preserve_formatting?` _bool_ - whither to preserve formatting
- `adjust_floating_point_error?` _bool_ - whether to adjust floating point error
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.dialects.ExcelDialect.sheet"></a>
#### <big>sheet</big>

```python
 | @Metadata.property
 | sheet()
```

**Returns**:

- `str|int` - sheet

<a name="frictionless.dialects.ExcelDialect.workbook_cache"></a>
#### <big>workbook\_cache</big>

```python
 | @Metadata.property
 | workbook_cache()
```

**Returns**:

- `dict` - workbook cache

<a name="frictionless.dialects.ExcelDialect.fill_merged_cells"></a>
#### <big>fill\_merged\_cells</big>

```python
 | @Metadata.property
 | fill_merged_cells()
```

**Returns**:

- `bool` - fill merged cells

<a name="frictionless.dialects.ExcelDialect.preserve_formatting"></a>
#### <big>preserve\_formatting</big>

```python
 | @Metadata.property
 | preserve_formatting()
```

**Returns**:

- `bool` - preserve formatting

<a name="frictionless.dialects.ExcelDialect.adjust_floating_point_error"></a>
#### <big>adjust\_floating\_point\_error</big>

```python
 | @Metadata.property
 | adjust_floating_point_error()
```

**Returns**:

- `bool` - adjust floating point error

<a name="frictionless.dialects.ExcelDialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.dialects.InlineDialect"></a>
### InlineDialect

```python
class InlineDialect(Dialect)
```

Inline dialect representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `keys?` _str[]_ - a list of strings to use as data keys
- `keyed?` _bool_ - whether data rows are keyed
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.dialects.InlineDialect.keys"></a>
#### <big>keys</big>

```python
 | @Metadata.property
 | keys()
```

**Returns**:

- `str[]?` - keys

<a name="frictionless.dialects.InlineDialect.keyed"></a>
#### <big>keyed</big>

```python
 | @Metadata.property
 | keyed()
```

**Returns**:

- `bool` - keyed

<a name="frictionless.dialects.InlineDialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.dialects.JsonDialect"></a>
### JsonDialect

```python
class JsonDialect(Dialect)
```

Json dialect representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `keys?` _str[]_ - a list of strings to use as data keys
- `keyed?` _bool_ - whether data rows are keyed
- `property?` _str_ - a path within JSON to the data
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.dialects.JsonDialect.keys"></a>
#### <big>keys</big>

```python
 | @Metadata.property
 | keys()
```

**Returns**:

- `str[]?` - keys

<a name="frictionless.dialects.JsonDialect.keyed"></a>
#### <big>keyed</big>

```python
 | @Metadata.property
 | keyed()
```

**Returns**:

- `bool` - keyed

<a name="frictionless.dialects.JsonDialect.property"></a>
#### <big>property</big>

```python
 | @Metadata.property
 | property()
```

**Returns**:

- `str?` - property

<a name="frictionless.dialects.JsonDialect.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.__main__"></a>
## frictionless.\_\_main\_\_

<a name="frictionless.server"></a>
## frictionless.server

<a name="frictionless.server.Server"></a>
### Server

```python
class Server()
```

Server representation

API      | Usage
-------- | --------
Public   | `from frictionless import Schema`

<a name="frictionless.server.Server.start"></a>
#### <big>start</big>

```python
 | start(port)
```

Start the server

**Arguments**:

- `port` _int_ - HTTP port

<a name="frictionless.server.Server.stop"></a>
#### <big>stop</big>

```python
 | stop()
```

Stop the server

<a name="frictionless.types"></a>
## frictionless.types

<a name="frictionless.types.yearmonth"></a>
## frictionless.types.yearmonth

<a name="frictionless.types.yearmonth.YearmonthType"></a>
### YearmonthType

```python
class YearmonthType(Type)
```

Yearmonth type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.datetime"></a>
## frictionless.types.datetime

<a name="frictionless.types.datetime.DatetimeType"></a>
### DatetimeType

```python
class DatetimeType(Type)
```

Datetime type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.date"></a>
## frictionless.types.date

<a name="frictionless.types.date.DateType"></a>
### DateType

```python
class DateType(Type)
```

Date type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.string"></a>
## frictionless.types.string

<a name="frictionless.types.string.StringType"></a>
### StringType

```python
class StringType(Type)
```

String type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.object"></a>
## frictionless.types.object

<a name="frictionless.types.object.ObjectType"></a>
### ObjectType

```python
class ObjectType(Type)
```

Object type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.geojson"></a>
## frictionless.types.geojson

<a name="frictionless.types.geojson.GeojsonType"></a>
### GeojsonType

```python
class GeojsonType(Type)
```

Geojson type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.year"></a>
## frictionless.types.year

<a name="frictionless.types.year.YearType"></a>
### YearType

```python
class YearType(Type)
```

Year type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.integer"></a>
## frictionless.types.integer

<a name="frictionless.types.integer.IntegerType"></a>
### IntegerType

```python
class IntegerType(Type)
```

Integer type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.time"></a>
## frictionless.types.time

<a name="frictionless.types.time.TimeType"></a>
### TimeType

```python
class TimeType(Type)
```

Time type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.geopoint"></a>
## frictionless.types.geopoint

<a name="frictionless.types.geopoint.GeopointType"></a>
### GeopointType

```python
class GeopointType(Type)
```

Geopoint type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.array"></a>
## frictionless.types.array

<a name="frictionless.types.array.ArrayType"></a>
### ArrayType

```python
class ArrayType(Type)
```

Array type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.boolean"></a>
## frictionless.types.boolean

<a name="frictionless.types.boolean.BooleanType"></a>
### BooleanType

```python
class BooleanType(Type)
```

Boolean type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.any"></a>
## frictionless.types.any

<a name="frictionless.types.any.AnyType"></a>
### AnyType

```python
class AnyType(Type)
```

Any type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.duration"></a>
## frictionless.types.duration

<a name="frictionless.types.duration.DurationType"></a>
### DurationType

```python
class DurationType(Type)
```

Duration type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.types.number"></a>
## frictionless.types.number

<a name="frictionless.types.number.NumberType"></a>
### NumberType

```python
class NumberType(Type)
```

Number type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

<a name="frictionless.loader"></a>
## frictionless.loader

<a name="frictionless.loader.Loader"></a>
### Loader

```python
class Loader()
```

Loader representation

API      | Usage
-------- | --------
Public   | `from frictionless import Loader`

**Arguments**:

- `file` _File_ - file

<a name="frictionless.loader.Loader.file"></a>
#### <big>file</big>

```python
 | @property
 | file()
```

**Returns**:

- `file` _File_ - file

<a name="frictionless.loader.Loader.byte_stream"></a>
#### <big>byte\_stream</big>

```python
 | @property
 | byte_stream()
```

File byte stream

The stream is available after opening the loader

**Returns**:

- `io.ByteStream` - file byte stream

<a name="frictionless.loader.Loader.text_stream"></a>
#### <big>text\_stream</big>

```python
 | @property
 | text_stream()
```

File text stream

The stream is available after opening the loader

**Returns**:

- `io.TextStream` - file text stream

<a name="frictionless.loader.Loader.open"></a>
#### <big>open</big>

```python
 | open()
```

Open the loader as "io.open" does

<a name="frictionless.loader.Loader.close"></a>
#### <big>close</big>

```python
 | close()
```

Close the loader as "filelike.close" does

<a name="frictionless.loader.Loader.closed"></a>
#### <big>closed</big>

```python
 | @property
 | closed()
```

Whether the loader is closed

**Returns**:

- `bool` - if closed

<a name="frictionless.loader.Loader.read_byte_stream"></a>
#### <big>read\_byte\_stream</big>

```python
 | read_byte_stream()
```

Read bytes stream

**Returns**:

- `io.ByteStream` - file byte stream

<a name="frictionless.loader.Loader.read_byte_stream_create"></a>
#### <big>read\_byte\_stream\_create</big>

```python
 | read_byte_stream_create()
```

Create bytes stream

**Returns**:

- `io.ByteStream` - file byte stream

<a name="frictionless.loader.Loader.read_byte_stream_infer_stats"></a>
#### <big>read\_byte\_stream\_infer\_stats</big>

```python
 | read_byte_stream_infer_stats(byte_stream)
```

Infer byte stream stats

**Arguments**:

- `byte_stream` _io.ByteStream_ - file byte stream
  

**Returns**:

- `io.ByteStream` - file byte stream

<a name="frictionless.loader.Loader.read_byte_stream_decompress"></a>
#### <big>read\_byte\_stream\_decompress</big>

```python
 | read_byte_stream_decompress(byte_stream)
```

Decompress byte stream

**Arguments**:

- `byte_stream` _io.ByteStream_ - file byte stream
  

**Returns**:

- `io.ByteStream` - file byte stream

<a name="frictionless.loader.Loader.read_text_stream"></a>
#### <big>read\_text\_stream</big>

```python
 | read_text_stream()
```

Read text stream

**Returns**:

- `io.TextStream` - file text stream

<a name="frictionless.loader.Loader.read_text_stream_infer_encoding"></a>
#### <big>read\_text\_stream\_infer\_encoding</big>

```python
 | read_text_stream_infer_encoding(byte_stream)
```

Infer text stream encoding

**Arguments**:

- `byte_stream` _io.ByteStream_ - file byte stream

<a name="frictionless.loader.Loader.read_text_stream_decode"></a>
#### <big>read\_text\_stream\_decode</big>

```python
 | read_text_stream_decode(byte_stream)
```

Decode text stream

**Arguments**:

- `byte_stream` _io.ByteStream_ - file byte stream
  

**Returns**:

- `text_stream` _io.TextStream_ - file text stream

<a name="frictionless.validate"></a>
## frictionless.validate

<a name="frictionless.validate.main"></a>
## frictionless.validate.main

<a name="frictionless.validate.main.validate"></a>
#### <big>validate</big>

```python
@Report.from_validate
validate(source, source_type=None, **options)
```

Validate resource

API      | Usage
-------- | --------
Public   | `from frictionless import validate`

**Arguments**:

- `source` _dict|str_ - a data source
- `source_type` _str_ - source type - inquiry, package, resource, schema or table
- `**options` _dict_ - options for the underlaying function
  

**Returns**:

- `Report` - validation report

<a name="frictionless.validate.table"></a>
## frictionless.validate.table

<a name="frictionless.validate.table.validate_table"></a>
#### <big>validate\_table</big>

```python
@Report.from_validate
validate_table(source, *, scheme=None, format=None, hashing=None, encoding=None, compression=None, compression_path=None, control=None, dialect=None, query=None, headers=None, schema=None, sync_schema=False, patch_schema=False, infer_type=None, infer_names=None, infer_volume=config.DEFAULT_INFER_VOLUME, infer_confidence=config.DEFAULT_INFER_CONFIDENCE, infer_missing_values=config.DEFAULT_MISSING_VALUES, lookup=None, checksum=None, extra_checks=None, pick_errors=None, skip_errors=None, limit_errors=None, limit_memory=config.DEFAULT_LIMIT_MEMORY)
```

Validate table

API      | Usage
-------- | --------
Public   | `from frictionless import validate_table`

**Arguments**:

  
- `source` _any_ - Source of the file; can be in various forms.
  Usually, it's a string as `<scheme>://path/to/file.<format>`.
  It also can be, for example, an array of data arrays/dictionaries.
  
- `scheme?` _str_ - Scheme for loading the file (file, http, ...).
  If not set, it'll be inferred from `source`.
  
- `format?` _str_ - File source's format (csv, xls, ...).
  If not set, it'll be inferred from `source`.
  
- `encoding?` _str_ - An algorithm to hash data.
  It defaults to 'md5'.
  
- `encoding?` _str_ - Source encoding.
  If not set, it'll be inferred from `source`.
  
- `compression?` _str_ - Source file compression (zip, ...).
  If not set, it'll be inferred from `source`.
  
- `compression_path?` _str_ - A path within the compressed file.
  It defaults to the first file in the archive.
  
- `control?` _dict|Control_ - File control.
  For more infromation, please check the Control documentation.
  
- `dialect?` _dict|Dialect_ - Table dialect.
  For more infromation, please check the Dialect documentation.
  
- `query?` _dict|Query_ - Table query.
  For more infromation, please check the Query documentation.
  
- `headers?` _int|int[]|[int[], str]_ - Either a row
  number or list of row numbers (in case of multi-line headers) to be
  considered as headers (rows start counting at 1), or a pair
  where the first element is header rows and the second the
  header joiner.  It defaults to 1.
  
- `schema?` _dict|Schema_ - Table schema.
  For more infromation, please check the Schema documentation.
  
- `sync_schema?` _bool_ - Whether to sync the schema.
  If it sets to `True` the provided schema will be mapped to
  the inferred schema. It means that, for example, you can
  provide a subset of fileds to be applied on top of the inferred
  fields or the provided schema can have different order of fields.
  
- `patch_schema?` _dict_ - A dictionary to be used as an inferred schema patch.
  The form of this dictionary should follow the Schema descriptor form
  except for the `fields` property which should be a mapping with the
  key named after a field name and the values being a field patch.
  For more information, please check "Extracting Data" guide.
  
- `infer_type?` _str_ - Enforce all the inferred types to be this type.
  For more information, please check "Describing  Data" guide.
  
- `infer_names?` _str[]_ - Enforce all the inferred fields to have provided names.
  For more information, please check "Describing  Data" guide.
  
- `infer_volume?` _int_ - The amount of rows to be extracted as a samle.
  For more information, please check "Describing  Data" guide.
  It defaults to 100
  
- `infer_confidence?` _float_ - A number from 0 to 1 setting the infer confidence.
  If  1 the data is guaranteed to be valid against the inferred schema.
  For more information, please check "Describing  Data" guide.
  It defaults to 0.9
  
- `infer_missing_values?` _str[]_ - String to be considered as missing values.
  For more information, please check "Describing  Data" guide.
  It defaults to `['']`
  
- `lookup?` _dict_ - The lookup is a special object providing relational information.
  For more information, please check "Extracting  Data" guide.
  
- `checksum?` _dict_ - a checksum dictionary
- `extra_checks?` _list_ - a list of extra checks
  pick_errors? ((str|int)[]): pick errors
  skip_errors? ((str|int)[]): skip errors
- `limit_errors?` _int_ - limit errors
- `limit_memory?` _int_ - limit memory
  

**Returns**:

- `Report` - validation report

<a name="frictionless.validate.package"></a>
## frictionless.validate.package

<a name="frictionless.validate.package.validate_package"></a>
#### <big>validate\_package</big>

```python
@Report.from_validate
validate_package(source, basepath=None, noinfer=False, **options)
```

Validate package

API      | Usage
-------- | --------
Public   | `from frictionless import validate_package`

**Arguments**:

- `source` _dict|str_ - a package descriptor
- `basepath?` _str_ - package basepath
- `noinfer?` _bool_ - don't call `package.infer`
- `**options` _dict_ - package options
  

**Returns**:

- `Report` - validation report

<a name="frictionless.validate.inquiry"></a>
## frictionless.validate.inquiry

<a name="frictionless.validate.inquiry.validate_inquiry"></a>
#### <big>validate\_inquiry</big>

```python
@Report.from_validate
validate_inquiry(source)
```

Validate inquiry

API      | Usage
-------- | --------
Public   | `from frictionless import validate_inquiry`

**Arguments**:

- `source` _dict|str_ - an inquiry descriptor
  

**Returns**:

- `Report` - validation report

<a name="frictionless.validate.schema"></a>
## frictionless.validate.schema

<a name="frictionless.validate.schema.validate_schema"></a>
#### <big>validate\_schema</big>

```python
@Report.from_validate
validate_schema(source)
```

Validate schema

API      | Usage
-------- | --------
Public   | `from frictionless import validate_schema`

**Arguments**:

- `source` _dict|str_ - a schema descriptor
  

**Returns**:

- `Report` - validation report

<a name="frictionless.validate.resource"></a>
## frictionless.validate.resource

<a name="frictionless.validate.resource.validate_resource"></a>
#### <big>validate\_resource</big>

```python
@Report.from_validate
validate_resource(source, basepath=None, noinfer=False, lookup=None, **options)
```

Validate resource

API      | Usage
-------- | --------
Public   | `from frictionless import validate_resource`

**Arguments**:

- `source` _dict|str_ - a resource descriptor
- `basepath?` _str_ - resource basepath
- `noinfer?` _bool_ - don't call `resource.infer`
- `lookup?` _dict_ - a lookup object
- `**options` _dict_ - resource options
  

**Returns**:

- `Report` - validation report

<a name="frictionless.controls"></a>
## frictionless.controls

<a name="frictionless.controls.Control"></a>
### Control

```python
class Control(Metadata)
```

Control representation

API      | Usage
-------- | --------
Public   | `from frictionless import controls`

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `detectEncoding?` _func_ - a function to detect encoding `(sample) -> encoding`
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.controls.Control.detect_encoding"></a>
#### <big>detect\_encoding</big>

```python
 | @Metadata.property
 | detect_encoding()
```

**Returns**:

- `func` - detect encoding function

<a name="frictionless.controls.LocalControl"></a>
### LocalControl

```python
class LocalControl(Control)
```

Local control representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.controls.RemoteControl"></a>
### RemoteControl

```python
class RemoteControl(Control)
```

Remote control representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
- `http_session?` _requests.Session_ - user defined HTTP session
- `http_preload?` _bool_ - don't use HTTP streaming and preload all the data
- `http_timeout?` _int_ - user defined HTTP timeout in minutes
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.controls.RemoteControl.http_session"></a>
#### <big>http\_session</big>

```python
 | @Metadata.property
 | http_session()
```

**Returns**:

- `requests.Session` - HTTP session

<a name="frictionless.controls.RemoteControl.http_preload"></a>
#### <big>http\_preload</big>

```python
 | @Metadata.property
 | http_preload()
```

**Returns**:

- `bool` - if not streaming

<a name="frictionless.controls.RemoteControl.http_timeout"></a>
#### <big>http\_timeout</big>

```python
 | @Metadata.property
 | http_timeout()
```

**Returns**:

- `int` - HTTP timeout in minutes

<a name="frictionless.controls.RemoteControl.expand"></a>
#### <big>expand</big>

```python
 | expand()
```

Expand metadata

<a name="frictionless.controls.StreamControl"></a>
### StreamControl

```python
class StreamControl(Control)
```

Stream control representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.controls.TextControl"></a>
### TextControl

```python
class TextControl(Control)
```

Text control representation

**Arguments**:

- `descriptor?` _str|dict_ - descriptor
  

**Raises**:

- `FrictionlessException` - raise any error that occurs during the process

<a name="frictionless.loaders"></a>
## frictionless.loaders

<a name="frictionless.loaders.remote"></a>
## frictionless.loaders.remote

<a name="frictionless.loaders.remote.RemoteLoader"></a>
### RemoteLoader

```python
class RemoteLoader(Loader)
```

Remote loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import loaders`

<a name="frictionless.loaders.stream"></a>
## frictionless.loaders.stream

<a name="frictionless.loaders.stream.StreamLoader"></a>
### StreamLoader

```python
class StreamLoader(Loader)
```

Stream loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import loaders`

<a name="frictionless.loaders.text"></a>
## frictionless.loaders.text

<a name="frictionless.loaders.text.TextLoader"></a>
### TextLoader

```python
class TextLoader(Loader)
```

Text loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import loaders`

<a name="frictionless.loaders.local"></a>
## frictionless.loaders.local

<a name="frictionless.loaders.local.LocalLoader"></a>
### LocalLoader

```python
class LocalLoader(Loader)
```

Local loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import loaders`

