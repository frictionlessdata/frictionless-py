---
title: API Referene
---

## frictionless.file

### File

```python
class File()
```

File representation

## frictionless.storage

### Storage

```python
class Storage()
```

Storage representation

## frictionless.pipeline

### Pipeline

```python
class Pipeline(Metadata)
```

Pipeline representation.

Arguments:

- `descriptor?` _str|dict_ - pipeline descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**tasks**

```python
 | @property
 | tasks()
```

Returns:

- `dict[]` - tasks

**run**

```python
 | run(*, parallel=False)
```

Run the pipeline

### PipelineTask

```python
class PipelineTask(Metadata)
```

Pipeline task representation.

Arguments:

- `descriptor?` _str|dict_ - pipeline task descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**run**

```python
 | run()
```

Run the task

## frictionless.status

### Status

```python
class Status(Metadata)
```

Status representation.

Arguments:

- `descriptor?` _str|dict_ - schema descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**version**

```python
 | @property
 | version()
```

Returns:

- `str` - frictionless version

**time**

```python
 | @property
 | time()
```

Returns:

- `float` - validation time

**valid**

```python
 | @property
 | valid()
```

Returns:

- `bool` - validation result

**stats**

```python
 | @property
 | stats()
```

Returns:

- `dict` - validation stats

**errors**

```python
 | @property
 | errors()
```

Returns:

- `Error[]` - validation errors

**tasks**

```python
 | @property
 | tasks()
```

Returns:

- `ReportTable[]` - validation tasks

**task**

```python
 | @property
 | task()
```

Returns:

- `ReportTable` - validation task (if there is only one)
  

Raises:

- `FrictionlessException` - if there are more that 1 task

### StatusTask

```python
class StatusTask(Metadata)
```

Status Task representation

**valid**

```python
 | @property
 | valid()
```

Returns:

- `bool` - validation result

**errors**

```python
 | @property
 | errors()
```

Returns:

- `Error[]` - validation errors

**target**

```python
 | @property
 | target()
```

Returns:

- `any` - validation target

**type**

```python
 | @property
 | type()
```

Returns:

- `any` - validation target

## frictionless.row

### Row

```python
class Row(dict)
```

Row representation

API      | Usage
-------- | --------
Public   | `from frictionless import Row`

> Constructor of this object is not Public API

This object is returned by `extract`, `resource.read_rows`, and other functions.


```python
rows = extract("data/table.csv")
for row in rows:
    # work with the Row
```

Arguments:

- `cells` _any[]_ - array of cells
- `field_info` _dict_ - special field info structure
- `row_position` _int_ - row position from 1
- `row_number` _int_ - row number from 1

**cells**

```python
 | @cached_property
 | cells()
```

Returns:

- `Field[]` - table schema fields

**fields**

```python
 | @cached_property
 | fields()
```

Returns:

- `Field[]` - table schema fields

**field\_names**

```python
 | @cached_property
 | field_names()
```

Returns:

- `Schema` - table schema

**field\_positions**

```python
 | @cached_property
 | field_positions()
```

Returns:

- `int[]` - table field positions

**row\_position**

```python
 | @cached_property
 | row_position()
```

Returns:

- `int` - row position from 1

**row\_number**

```python
 | @cached_property
 | row_number()
```

Returns:

- `int` - row number from 1

**blank\_cells**

```python
 | @cached_property
 | blank_cells()
```

A mapping indexed by a field name with blank cells before parsing

Returns:

- `dict` - row blank cells

**error\_cells**

```python
 | @cached_property
 | error_cells()
```

A mapping indexed by a field name with error cells before parsing

Returns:

- `dict` - row error cells

**errors**

```python
 | @cached_property
 | errors()
```

Returns:

- `Error[]` - row errors

**valid**

```python
 | @cached_property
 | valid()
```

Returns:

- `bool` - if row valid

**to\_str**

```python
 | to_str()
```

Returns:

- `str` - a row as a CSV string

**to\_list**

```python
 | to_list(*, json=False, types=None)
```

Arguments:

- `json` _bool_ - make data types compatible with JSON format
- `types` _str[]_ - list of supported types
  

Returns:

- `dict` - a row as a list

**to\_dict**

```python
 | to_dict(*, json=False, types=None)
```

Arguments:

- `json` _bool_ - make data types compatible with JSON format
  

Returns:

- `dict` - a row as a dictionary

## frictionless.checks

## frictionless.checks.checksum

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

Arguments:

- `descriptor` _dict_ - check's descriptor
- `descriptor.hash?` _str_ - a hash sum of the table's bytes
- `descriptor.bytes?` _int_ - number of bytes
- `descriptor.fields?` _int_ - number of fields
- `descriptor.rows?` _int_ - number of rows

## frictionless.checks.regulation

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

Arguments:

- `descriptor` _dict_ - check's descriptor
- `descriptor.fieldName` _str_ - a field name to look into
- `descriptor.blacklist` _any[]_ - a list of forbidden values

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

Arguments:

- `descriptor` _dict_ - check's descriptor
- `descriptor.fieldName` _str_ - a field name to check

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

Arguments:

- `descriptor` _dict_ - check's descriptor
- `descriptor.constraint` _str_ - a python expression to evaluate against a row

## frictionless.checks.baseline

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

## frictionless.checks.heuristic

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

Arguments:

- `descriptor` _dict_ - check's descriptor
- `descriptor.fieldName` _str_ - a field name to check
- `descriptor.average?` _str_ - one of "mean", "median" or "mode" (default: "mean")
- `descriptor.interval?` _str_ - statistical interval (default: 3)

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

## frictionless.package

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

Arguments:

- `descriptor?` _str|dict_ - package descriptor
- `resources?` _dict|Resource[]_ - list of resource descriptors
- `name?` _str_ - package name (for machines)
- `id?` _str_ - package id (for machines)
- `licenses?` _dict[]_ - package licenses
- `profile?` _str_ - profile name like 'data-package'
- `title?` _str_ - package title (for humans)
- `description?` _str_ - package description
- `homepage?` _str_ - package homepage
- `version?` _str_ - package version
- `sources?` _dict[]_ - package sources
- `contributors?` _dict[]_ - package contributors
- `keywords?` _str[]_ - package keywords
- `image?` _str_ - package image
- `created?` _str_ - package created
- `hashing?` _str_ - a hashing algorithm for resources
- `basepath?` _str_ - a basepath of the package
- `onerror?` _ignore|warn|raise_ - behaviour if there is an error
- `trusted?` _bool_ - don't raise an exception on unsafe paths
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**name**

```python
 | @Metadata.property
 | name()
```

Returns:

- `str?` - package name

**id**

```python
 | @Metadata.property
 | id()
```

Returns:

- `str?` - package id

**licenses**

```python
 | @Metadata.property
 | licenses()
```

Returns:

- `dict?` - package licenses

**profile**

```python
 | @Metadata.property
 | profile()
```

Returns:

- `str` - package profile

**title**

```python
 | @Metadata.property
 | title()
```

Returns:

- `str?` - package title

**description**

```python
 | @Metadata.property
 | description()
```

Returns:

- `str?` - package description

**homepage**

```python
 | @Metadata.property
 | homepage()
```

Returns:

- `str?` - package homepage

**version**

```python
 | @Metadata.property
 | version()
```

Returns:

- `str?` - package version

**sources**

```python
 | @Metadata.property
 | sources()
```

Returns:

- `dict[]?` - package sources

**contributors**

```python
 | @Metadata.property
 | contributors()
```

Returns:

- `dict[]?` - package contributors

**keywords**

```python
 | @Metadata.property
 | keywords()
```

Returns:

- `str[]?` - package keywords

**image**

```python
 | @Metadata.property
 | image()
```

Returns:

- `str?` - package image

**created**

```python
 | @Metadata.property
 | created()
```

Returns:

- `str?` - package created

**hashing**

```python
 | @Metadata.property(cache=False, write=False)
 | hashing()
```

Returns:

- `str` - package hashing

**basepath**

```python
 | @Metadata.property(cache=False, write=False)
 | basepath()
```

Returns:

- `str` - package basepath

**onerror**

```python
 | @Metadata.property(cache=False, write=False)
 | onerror()
```

Returns:

- `ignore|warn|raise` - on error bahaviour

**trusted**

```python
 | @Metadata.property(cache=False, write=False)
 | trusted()
```

Returns:

- `str` - package trusted

**resources**

```python
 | @Metadata.property
 | resources()
```

Returns:

- `Resources[]` - package resource

**resource\_names**

```python
 | @Metadata.property(cache=False, write=False)
 | resource_names()
```

Returns:

- `str[]` - package resource names

**add\_resource**

```python
 | add_resource(descriptor)
```

Add new resource to package.

Arguments:

- `descriptor` _dict_ - resource descriptor
  

Returns:

- `Resource/None` - added `Resource` instance or `None` if not added

**get\_resource**

```python
 | get_resource(name)
```

Get resource by name.

Arguments:

- `name` _str_ - resource name
  

Raises:

- `FrictionlessException` - if resource is not found
  

Returns:

- `Resource/None` - `Resource` instance or `None` if not found

**has\_resource**

```python
 | has_resource(name)
```

Check if a resource is present

Arguments:

- `name` _str_ - schema resource name
  

Returns:

- `bool` - whether there is the resource

**remove\_resource**

```python
 | remove_resource(name)
```

Remove resource by name.

Arguments:

- `name` _str_ - resource name
  

Raises:

- `FrictionlessException` - if resource is not found
  

Returns:

- `Resource/None` - removed `Resource` instances or `None` if not found

**expand**

```python
 | expand()
```

Expand metadata

It will add default values to the package.

**infer**

```python
 | infer(*, stats=False)
```

Infer package's attributes

Arguments:

- `stats?` _bool_ - stream files completely and infer stats

**from\_zip**

```python
 | @staticmethod
 | from_zip(path, **options)
```

Create a package from ZIP

**from\_storage**

```python
 | @staticmethod
 | from_storage(storage)
```

Import package from storage

Arguments:

- `storage` _Storage_ - storage instance

**from\_ckan**

```python
 | @staticmethod
 | from_ckan(*, url, dataset, apikey=None)
```

Import package from CKAN

Arguments:

- `url` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dataset` _string_ - dataset id in CKAN e.g. "my-dataset"
- `apikey?` _str_ - API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"

**from\_sql**

```python
 | @staticmethod
 | from_sql(*, url=None, engine=None, prefix="", namespace=None)
```

Import package from SQL

Arguments:

- `url?` _string_ - SQL connection string
- `engine?` _object_ - `sqlalchemy` engine
- `prefix?` _str_ - prefix for all tables
- `namespace?` _str_ - SQL scheme

**from\_pandas**

```python
 | @staticmethod
 | from_pandas(*, dataframes)
```

Import package from Pandas dataframes

Arguments:

- `dataframes` _dict_ - mapping of Pandas dataframes

**from\_spss**

```python
 | @staticmethod
 | from_spss(*, basepath)
```

Import package from SPSS directory

Arguments:

- `basepath` _str_ - SPSS dir path

**from\_bigquery**

```python
 | @staticmethod
 | from_bigquery(*, service, project, dataset, prefix="")
```

Import package from Bigquery

Arguments:

- `service` _object_ - BigQuery `Service` object
- `project` _str_ - BigQuery project name
- `dataset` _str_ - BigQuery dataset name
- `prefix?` _str_ - prefix for all names

**to\_copy**

```python
 | to_copy()
```

Create a copy of the package

**to\_zip**

```python
 | to_zip(path, *, resolve=[], encoder_class=None)
```

Save package to a zip

Arguments:

- `path` _str_ - target path
- `resolve` _str[]_ - Data sources to resolve.
  For "memory" data it means saving them as CSV and including into ZIP.
  For "remote" data it means downloading them and including into ZIP.
  For example, `resolve=["memory", "remote"]`
- `encoder_class` _object_ - json encoder class
  

Raises:

- `FrictionlessException` - on any error

**to\_storage**

```python
 | to_storage(storage, *, force=False)
```

Export package to storage

Arguments:

- `storage` _Storage_ - storage instance
- `force` _bool_ - overwrite existent

**to\_ckan**

```python
 | to_ckan(*, url, dataset, apikey=None, force=False)
```

Export package to CKAN

Arguments:

- `url` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dataset` _string_ - dataset id in CKAN e.g. "my-dataset"
- `apikey?` _str_ - API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
- `force` _bool_ - (optional) overwrite existing data

**to\_sql**

```python
 | to_sql(*, url=None, engine=None, prefix="", namespace=None, force=False)
```

Export package to SQL

Arguments:

- `url?` _string_ - SQL connection string
- `engine?` _object_ - `sqlalchemy` engine
- `prefix?` _str_ - prefix for all tables
- `namespace?` _str_ - SQL scheme
- `force` _bool_ - overwrite existent

**to\_pandas**

```python
 | to_pandas()
```

Export package to Pandas dataframes

**to\_spss**

```python
 | to_spss(*, basepath, force=False)
```

Export package to SPSS directory

Arguments:

- `basepath` _str_ - SPSS dir path
- `force` _bool_ - overwrite existent

**to\_bigquery**

```python
 | to_bigquery(*, service, project, dataset, prefix="", force=False)
```

Export package to Bigquery

Arguments:

- `service` _object_ - BigQuery `Service` object
- `project` _str_ - BigQuery project name
- `dataset` _str_ - BigQuery dataset name
- `prefix?` _str_ - prefix for all names
- `force` _bool_ - overwrite existent

## frictionless.plugin

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

**create\_check**

```python
 | create_check(name, *, descriptor=None)
```

Create checks

Arguments:

- `name` _str_ - check name
- `descriptor` _dict_ - check descriptor
  

Returns:

- `Check` - check

**create\_control**

```python
 | create_control(file, *, descriptor)
```

Create control

Arguments:

- `file` _File_ - control file
- `descriptor` _dict_ - control descriptor
  

Returns:

- `Control` - control

**create\_dialect**

```python
 | create_dialect(file, *, descriptor)
```

Create dialect

Arguments:

- `file` _File_ - dialect file
- `descriptor` _dict_ - dialect descriptor
  

Returns:

- `Dialect` - dialect

**create\_loader**

```python
 | create_loader(file)
```

Create loader

Arguments:

- `file` _File_ - loader file
  

Returns:

- `Loader` - loader

**create\_parser**

```python
 | create_parser(file)
```

Create parser

Arguments:

- `file` _File_ - parser file
  

Returns:

- `Parser` - parser

**create\_server**

```python
 | create_server(name)
```

Create server

Arguments:

- `name` _str_ - server name
  

Returns:

- `Server` - server

## frictionless.program

## frictionless.program.main

**program\_main**

```python
@program.callback()
program_main(version: Optional[bool] = typer.Option(None, "--version", callback=version))
```

Describe, extract, validate and transform tabular data.

## frictionless.program.validate

**program\_validate**

```python
@program.command(name="validate")
program_validate(source: List[str] = Arg(None, help="Data source to describe [default: stdin]"), type: str = Opt(None, help='Specify source type e.g. "package"'), scheme: str = Opt(None, help="Specify schema  [default: inferred]"), format: str = Opt(None, help="Specify format  [default: inferred]"), hashing: str = Opt(None, help="Specify hashing algorithm  [default: inferred]"), encoding: str = Opt(None, help="Specify encoding  [default: inferred]"), innerpath: str = Opt(None, help="Specify in-archive path  [default: first]"), compression: str = Opt(None, help="Specify compression  [default: inferred]"), header_rows: str = Opt(None, help="Comma-separated row numbers  [default: 1]"), header_join: str = Opt(None, help="A separator to join a multiline header"), pick_fields: str = Opt(None, help='Comma-separated fields to pick e.g. "1,name1"'), skip_fields: str = Opt(None, help='Comma-separated fields to skip e.g. "2,name2"'), limit_fields: int = Opt(None, help="Limit fields by this integer"), offset_fields: int = Opt(None, help="Offset fields by this integer"), pick_rows: str = Opt(None, help='Comma-separated rows to pick e.g. "1,<blank>"'), skip_rows: str = Opt(None, help='Comma-separated rows to skip e.g. "2,3,4,5"'), limit_rows: int = Opt(None, help="Limit rows by this integer"), offset_rows: int = Opt(None, help="Offset rows by this integer"), schema: str = Opt(None, help="Specify a path to a schema"), sync_schema: bool = Opt(None, help="Sync the schema based on headers"), infer_type: str = Opt(None, help="Force all the fields to have this type"), infer_names: str = Opt(None, help="Comma-separated list of field names"), infer_volume: int = Opt(None, help="Limit data sample size by this integer"), infer_confidence: float = Opt(None, help="A float from 0 to 1"), infer_missing_values: str = Opt(None, help="Comma-separated list of missing values"), basepath: str = Opt(None, help="Basepath of the resource/package"), parallel: bool = Opt(None, help="Enable multiprocessing"), checksum_hash: str = Opt(None, help="Expected hash based on hashing option"), checksum_bytes: int = Opt(None, help="Expected size in bytes"), checksum_rows: int = Opt(None, help="Expected amoutn of rows"), pick_errors: str = Opt(None, help='Comma-separated errors to pick e.g. "type-error"'), skip_errors: str = Opt(None, help='Comma-separated errors to skip e.g. "blank-row"'), limit_errors: int = Opt(None, help="Limit errors by this integer"), limit_memory: int = Opt(None, help="Limit memory by this integer in MB"), yaml: bool = Opt(False, help="Return in pure YAML format"), json: bool = Opt(False, help="Return in JSON format"))
```

Validate a data source.

Based on the inferred data source type it will validate resource or package.
Default output format is YAML with a front matter.

## frictionless.program.transform

**program\_transform**

```python
@program.command(name="transform")
program_transform(source: str = Arg(None, help="Path to a transform pipeline [default: stdin]"))
```

Transform data source using a provided pipeline.

## frictionless.program.describe

**program\_describe**

```python
@program.command(name="describe")
program_describe(source: List[str] = Arg(None, help="Data source to describe [default: stdin]"), type: str = Opt(None, help='Specify source type e.g. "package"'), scheme: str = Opt(None, help="Specify schema  [default: inferred]"), format: str = Opt(None, help="Specify format  [default: inferred]"), hashing: str = Opt(None, help="Specify hashing algorithm  [default: inferred]"), encoding: str = Opt(None, help="Specify encoding  [default: inferred]"), innerpath: str = Opt(None, help="Specify in-archive path  [default: first]"), compression: str = Opt(None, help="Specify compression  [default: inferred]"), header_rows: str = Opt(None, help="Comma-separated row numbers  [default: 1]"), header_join: str = Opt(None, help="A separator to join a multiline header"), pick_fields: str = Opt(None, help='Comma-separated fields to pick e.g. "1,name1"'), skip_fields: str = Opt(None, help='Comma-separated fields to skip e.g. "2,name2"'), limit_fields: int = Opt(None, help="Limit fields by this integer"), offset_fields: int = Opt(None, help="Offset fields by this integer"), pick_rows: str = Opt(None, help='Comma-separated rows to pick e.g. "1,<blank>"'), skip_rows: str = Opt(None, help='Comma-separated rows to skip e.g. "2,3,4,5"'), limit_rows: int = Opt(None, help="Limit rows by this integer"), offset_rows: int = Opt(None, help="Offset rows by this integer"), infer_type: str = Opt(None, help="Force all the fields to have this type"), infer_names: str = Opt(None, help="Comma-separated list of field names"), infer_volume: int = Opt(None, help="Limit data sample size by this integer"), infer_confidence: float = Opt(None, help="A float from 0 to 1"), infer_missing_values: str = Opt(None, help="Comma-separated list of missing values"), basepath: str = Opt(None, help="Basepath of the resource/package"), expand: bool = Opt(None, help="Expand default values"), nostats: bool = Opt(None, help="Do not infer stats"), yaml: bool = Opt(False, help="Return in pure YAML format"), json: bool = Opt(False, help="Return in JSON format"))
```

Describe a data source.

Based on the inferred data source type it will return resource or package descriptor.
Default output format is YAML with a front matter.

## frictionless.program.api

**program\_api**

```python
@program.command(name="api")
program_api(port: int = Opt(config.DEFAULT_SERVER_PORT, help="Specify server port"))
```

Start API server

## frictionless.program.extract

**program\_extract**

```python
@program.command(name="extract")
program_extract(source: List[str] = Arg(None, help="Data source to describe [default: stdin]"), type: str = Opt(None, help='Specify source type e.g. "package"'), scheme: str = Opt(None, help="Specify schema  [default: inferred]"), format: str = Opt(None, help="Specify format  [default: inferred]"), hashing: str = Opt(None, help="Specify hashing algorithm  [default: inferred]"), encoding: str = Opt(None, help="Specify encoding  [default: inferred]"), innerpath: str = Opt(None, help="Specify in-archive path  [default: first]"), compression: str = Opt(None, help="Specify compression  [default: inferred]"), header_rows: str = Opt(None, help="Comma-separated row numbers  [default: 1]"), header_join: str = Opt(None, help="A separator to join a multiline header"), pick_fields: str = Opt(None, help='Comma-separated fields to pick e.g. "1,name1"'), skip_fields: str = Opt(None, help='Comma-separated fields to skip e.g. "2,name2"'), limit_fields: int = Opt(None, help="Limit fields by this integer"), offset_fields: int = Opt(None, help="Offset fields by this integer"), pick_rows: str = Opt(None, help='Comma-separated rows to pick e.g. "1,<blank>"'), skip_rows: str = Opt(None, help='Comma-separated rows to skip e.g. "2,3,4,5"'), limit_rows: int = Opt(None, help="Limit rows by this integer"), offset_rows: int = Opt(None, help="Offset rows by this integer"), schema: str = Opt(None, help="Specify a path to a schema"), sync_schema: bool = Opt(None, help="Sync the schema based on headers"), infer_type: str = Opt(None, help="Force all the fields to have this type"), infer_names: str = Opt(None, help="Comma-separated list of field names"), infer_volume: int = Opt(None, help="Limit data sample size by this integer"), infer_confidence: float = Opt(None, help="A float from 0 to 1"), infer_missing_values: str = Opt(None, help="Comma-separated list of missing values"), basepath: str = Opt(None, help="Basepath of the resource/package"), yaml: bool = Opt(False, help="Return in pure YAML format"), json: bool = Opt(False, help="Return in JSON format"), csv: bool = Opt(False, help="Return in CSV format"))
```

Extract a data source.

Based on the inferred data source type it will return resource or package data.
Default output format is tabulated with a front matter.

## frictionless.type

### Type

```python
class Type()
```

Data type representation

API      | Usage
-------- | --------
Public   | `from frictionless import Type`

This class is for subclassing.

Arguments:

- `field` _Field_ - field

**supported\_constraints**

Returns:

- `str[]` - a list of supported constraints

**field**

```python
 | @cached_property
 | field()
```

Returns:

- `Field` - field

**read\_cell**

```python
 | read_cell(cell)
```

Convert cell (read direction)

Arguments:

- `cell` _any_ - cell to covert
  

Returns:

- `any` - converted cell

**write\_cell**

```python
 | write_cell(cell)
```

Convert cell (write direction)

Arguments:

- `cell` _any_ - cell to covert
  

Returns:

- `any` - converted cell

## frictionless.metadata

### Metadata

```python
class Metadata(helpers.ControlledDict)
```

Metadata representation

API      | Usage
-------- | --------
Public   | `from frictionless import Metadata`

Arguments:

- `descriptor?` _str|dict_ - metadata descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**setinitial**

```python
 | setinitial(key, value)
```

Set an initial item in a subclass' constructor

Arguments:

- `key` _str_ - key
- `value` _any_ - value

**to\_copy**

```python
 | to_copy()
```

Create a copy of the metadata

Returns:

- `Metadata` - a copy of the metadata

**to\_dict**

```python
 | to_dict()
```

Convert metadata to a dict

Returns:

- `dict` - metadata as a dict

**to\_json**

```python
 | to_json(path=None, encoder_class=None)
```

Save metadata as a json

Arguments:

- `path` _str_ - target path
  

Raises:

- `FrictionlessException` - on any error

**to\_yaml**

```python
 | to_yaml(path=None)
```

Save metadata as a yaml

Arguments:

- `path` _str_ - target path
  

Raises:

- `FrictionlessException` - on any error

**metadata\_valid**

```python
 | @property
 | metadata_valid()
```

Returns:

- `bool` - whether the metadata is valid

**metadata\_errors**

```python
 | @property
 | metadata_errors()
```

Returns:

- `Errors[]` - a list of the metadata errors

**metadata\_attach**

```python
 | metadata_attach(name, value)
```

Helper method for attaching a value to  the metadata

Arguments:

- `name` _str_ - name
- `value` _any_ - value

**metadata\_extract**

```python
 | metadata_extract(descriptor)
```

Helper method called during the metadata extraction

Arguments:

- `descriptor` _any_ - descriptor

**metadata\_process**

```python
 | metadata_process()
```

Helper method called on any metadata change

**metadata\_validate**

```python
 | metadata_validate(profile=None)
```

Helper method called on any metadata change

Arguments:

- `profile` _dict_ - a profile to validate against of

**property**

```python
 | @staticmethod
 | property(func=None, *, cache=True, reset=True, write=True)
```

Create a metadata property

Arguments:

- `func` _func_ - method
- `cache?` _bool_ - cache
- `reset?` _bool_ - reset
- `write?` _func_ - write

## frictionless.field

### Field

```python
class Field(Metadata)
```

Field representation

API      | Usage
-------- | --------
Public   | `from frictionless import Field`

Arguments:

- `descriptor?` _str|dict_ - field descriptor
- `name?` _str_ - field name (for machines)
- `title?` _str_ - field title (for humans)
- `descriptor?` _str_ - field descriptor
- `type?` _str_ - field type e.g. `string`
- `format?` _str_ - field format e.g. `default`
- `missing_values?` _str[]_ - missing values
- `constraints?` _dict_ - constraints
- `rdf_type?` _str_ - RDF type
- `schema?` _Schema_ - parent schema object
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**name**

```python
 | @Metadata.property
 | name()
```

Returns:

- `str` - name

**title**

```python
 | @Metadata.property
 | title()
```

Returns:

- `str?` - title

**description**

```python
 | @Metadata.property
 | description()
```

Returns:

- `str?` - description

**type**

```python
 | @Metadata.property
 | type()
```

Returns:

- `str` - type

**format**

```python
 | @Metadata.property
 | format()
```

Returns:

- `str` - format

**missing\_values**

```python
 | @Metadata.property
 | missing_values()
```

Returns:

- `str[]` - missing values

**constraints**

```python
 | @Metadata.property
 | constraints()
```

Returns:

- `dict` - constraints

**rdf\_type**

```python
 | @Metadata.property
 | rdf_type()
```

Returns:

- `str?` - RDF Type

**required**

```python
 | @Metadata.property(
 |         write=lambda self, value: setitem(self.constraints, "required", value)
 |     )
 | required()
```

Returns:

- `bool` - if field is requried

**schema**

```python
 | @property
 | schema()
```

Returns:

- `Schema?` - parent schema

**true\_values**

```python
 | @Metadata.property
 | true_values()
```

Returns:

- `str[]` - true values

**false\_values**

```python
 | @Metadata.property
 | false_values()
```

Returns:

- `str[]` - false values

**bare\_number**

```python
 | @Metadata.property
 | bare_number()
```

Returns:

- `bool` - if a bare number

**float\_number**

```python
 | @Metadata.property
 | float_number()
```

Returns:

- `bool` - whether it's a floating point number

**decimal\_char**

```python
 | @Metadata.property
 | decimal_char()
```

Returns:

- `str` - decimal char

**group\_char**

```python
 | @Metadata.property
 | group_char()
```

Returns:

- `str` - group char

**expand**

```python
 | expand()
```

Expand metadata

**read\_cell**

```python
 | read_cell(cell)
```

Read cell

Arguments:

- `cell` _any_ - cell
  

Returns:

  (any, OrderedDict): processed cell and dict of notes

**read\_cell\_convert**

```python
 | read_cell_convert(cell)
```

Read cell (convert only)

Arguments:

- `cell` _any_ - cell
  

Returns:

- `any/None` - processed cell or None if an error

**read\_cell\_checks**

```python
 | @Metadata.property(write=False)
 | read_cell_checks()
```

Read cell (checks only)

Returns:

- `OrderedDict` - dictionlary of check function by a constraint name

**write\_cell**

```python
 | write_cell(cell, *, ignore_missing=False)
```

Write cell

Arguments:

- `cell` _any_ - cell to convert
- `ignore_missing?` _bool_ - don't convert None values
  

Returns:

  (any, OrderedDict): processed cell and dict of notes

**write\_cell\_convert**

```python
 | write_cell_convert(cell)
```

Write cell (convert only)

Arguments:

- `cell` _any_ - cell
  

Returns:

- `any/None` - processed cell or None if an error

**write\_cell\_missing\_value**

```python
 | @Metadata.property(write=False)
 | write_cell_missing_value()
```

Write cell (missing value only)

Returns:

- `str` - a value to replace None cells

## frictionless.steps

## frictionless.steps.table

## frictionless.steps.row

## frictionless.steps.field

## frictionless.steps.cell

## frictionless.steps.resource

## frictionless.system

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

**register**

```python
 | register(name, plugin)
```

Register a plugin

Arguments:

- `name` _str_ - plugin name
- `plugin` _Plugin_ - plugin to register

**create\_check**

```python
 | create_check(name, *, descriptor=None)
```

Create checks

Arguments:

- `name` _str_ - check name
- `descriptor` _dict_ - check descriptor
  

Returns:

- `Check` - check

**create\_control**

```python
 | create_control(resource, *, descriptor)
```

Create control

Arguments:

- `resource` _Resource_ - control resource
- `descriptor` _dict_ - control descriptor
  

Returns:

- `Control` - control

**create\_dialect**

```python
 | create_dialect(resource, *, descriptor)
```

Create dialect

Arguments:

- `resource` _Resource_ - dialect resource
- `descriptor` _dict_ - dialect descriptor
  

Returns:

- `Dialect` - dialect

**create\_file**

```python
 | create_file(source, **options)
```

Create file

Arguments:

- `source` _any_ - file source
- `options` _dict_ - file options
  

Returns:

- `File` - file

**create\_loader**

```python
 | create_loader(resource)
```

Create loader

Arguments:

- `resource` _Resource_ - loader resource
  

Returns:

- `Loader` - loader

**create\_parser**

```python
 | create_parser(resource)
```

Create parser

Arguments:

- `resource` _Resource_ - parser resource
  

Returns:

- `Parser` - parser

**create\_server**

```python
 | create_server(name, **options)
```

Create server

Arguments:

- `name` _str_ - server name
- `options` _str_ - server options
  

Returns:

- `Server` - server

**create\_storage**

```python
 | create_storage(name, **options)
```

Create storage

Arguments:

- `name` _str_ - storage name
- `options` _str_ - storage options
  

Returns:

- `Storage` - storage

**create\_type**

```python
 | create_type(field)
```

Create checks

Arguments:

- `field` _Field_ - corresponding field
  

Returns:

- `Type` - type

## frictionless.helpers

## frictionless.inquiry

### Inquiry

```python
class Inquiry(Metadata)
```

Inquiry representation.

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**tasks**

```python
 | @property
 | tasks()
```

Returns:

- `dict[]` - tasks

### InquiryTask

```python
class InquiryTask(Metadata)
```

Inquiry task representation.

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**source**

```python
 | @property
 | source()
```

Returns:

- `any` - source

**type**

```python
 | @property
 | type()
```

Returns:

- `string?` - type

## frictionless.config

## frictionless.header

### Header

```python
class Header(list)
```

Header representation

API      | Usage
-------- | --------
Public   | `from frictionless import Header`

> Constructor of this object is not Public API

Arguments:

- `labels` _any[]_ - header row labels
- `fields` _Field[]_ - table fields
- `field_positions` _int[]_ - field positions
- `row_positions` _int[]_ - row positions
- `ignore_case` _bool_ - ignore case

**fields**

```python
 | @cached_property
 | fields()
```

Returns:

- `Schema` - table fields

**field\_names**

```python
 | @cached_property
 | field_names()
```

Returns:

- `str[]` - table field names

**field\_positions**

```python
 | @cached_property
 | field_positions()
```

Returns:

- `int[]` - table field positions

**row\_positions**

```python
 | @cached_property
 | row_positions()
```

Returns:

- `int[]` - table row positions

**missing**

```python
 | @cached_property
 | missing()
```

Returns:

- `bool` - if there is not header

**errors**

```python
 | @cached_property
 | errors()
```

Returns:

- `Error[]` - header errors

**valid**

```python
 | @cached_property
 | valid()
```

Returns:

- `bool` - if header valid

**to\_str**

```python
 | to_str()
```

Returns:

- `str` - a row as a CSV string

**to\_list**

```python
 | to_list()
```

Convert to a list

## frictionless.plugins

## frictionless.plugins.remote

### RemotePlugin

```python
class RemotePlugin(Plugin)
```

Plugin for Remote Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.remote import RemotePlugin`

### RemoteControl

```python
class RemoteControl(Control)
```

Remote control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.remote import RemoteControl`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `http_session?` _requests.Session_ - user defined HTTP session
- `http_preload?` _bool_ - don't use HTTP streaming and preload all the data
- `http_timeout?` _int_ - user defined HTTP timeout in minutes
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**http\_session**

```python
 | @Metadata.property
 | http_session()
```

Returns:

- `requests.Session` - HTTP session

**http\_preload**

```python
 | @Metadata.property
 | http_preload()
```

Returns:

- `bool` - if not streaming

**http\_timeout**

```python
 | @Metadata.property
 | http_timeout()
```

Returns:

- `int` - HTTP timeout in minutes

**expand**

```python
 | expand()
```

Expand metadata

### RemoteLoader

```python
class RemoteLoader(Loader)
```

Remote loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.remote import RemoteLoader`

## frictionless.plugins.pandas

### PandasPlugin

```python
class PandasPlugin(Plugin)
```

Plugin for Pandas

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasPlugin`

### PandasDialect

```python
class PandasDialect(Dialect)
```

Pandas dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### PandasParser

```python
class PandasParser(Parser)
```

Pandas parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasParser`

### PandasStorage

```python
class PandasStorage(Storage)
```

Pandas storage implementation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.pandas import PandasStorage`

Arguments:

- `dataframes?` _dict_ - dictionary of Pandas dataframes

## frictionless.plugins.spss

### SpssPlugin

```python
class SpssPlugin(Plugin)
```

Plugin for SPSS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssPlugin`

### SpssDialect

```python
class SpssDialect(Dialect)
```

Spss dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### SpssParser

```python
class SpssParser(Parser)
```

Spss parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssParser`

### SpssStorage

```python
class SpssStorage(Storage)
```

SPSS storage implementation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.spss import SpssStorage`

Arguments:

- `basepath?` _str_ - A path to a dir for reading/writing SAV files.
  Defaults to current dir.

## frictionless.plugins.bigquery

### BigqueryPlugin

```python
class BigqueryPlugin(Plugin)
```

Plugin for BigQuery

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryPlugin`

### BigqueryDialect

```python
class BigqueryDialect(Dialect)
```

Bigquery dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `project` _str_ - project
- `dataset?` _str_ - dataset
- `table?` _str_ - table
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### BigqueryParser

```python
class BigqueryParser(Parser)
```

Bigquery parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryParser`

### BigqueryStorage

```python
class BigqueryStorage(Storage)
```

BigQuery storage implementation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.bigquery import BigqueryStorage`

Arguments:

- `service` _object_ - BigQuery `Service` object
- `project` _str_ - BigQuery project name
- `dataset` _str_ - BigQuery dataset name
- `prefix?` _str_ - prefix for all names

## frictionless.plugins.s3

### S3Plugin

```python
class S3Plugin(Plugin)
```

Plugin for S3

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.s3 import S3Plugin`

### S3Control

```python
class S3Control(Control)
```

S3 control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.s3 import S3Control`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `endpoint_url?` _string_ - endpoint url
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**expand**

```python
 | expand()
```

Expand metadata

### S3Loader

```python
class S3Loader(Loader)
```

S3 loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.s3 import S3Loader`

## frictionless.plugins.ods

### OdsPlugin

```python
class OdsPlugin(Plugin)
```

Plugin for ODS

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsPlugin`

### OdsDialect

```python
class OdsDialect(Dialect)
```

Ods dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `sheet?` _str_ - sheet
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**sheet**

```python
 | @Metadata.property
 | sheet()
```

Returns:

- `int|str` - sheet

**expand**

```python
 | expand()
```

Expand metadata

### OdsParser

```python
class OdsParser(Parser)
```

ODS parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ods import OdsParser`

## frictionless.plugins.filelike

### FilelikePlugin

```python
class FilelikePlugin(Plugin)
```

Plugin for Local Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.filelike import FilelikePlugin`

### FilelikeControl

```python
class FilelikeControl(Control)
```

Filelike control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.filelike import FilelikeControl`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### FilelikeLoader

```python
class FilelikeLoader(Loader)
```

Filelike loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.filelike import FilelikeLoader`

## frictionless.plugins.excel

### ExcelPlugin

```python
class ExcelPlugin(Plugin)
```

Plugin for Excel

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import ExcelPlugin`

### ExcelDialect

```python
class ExcelDialect(Dialect)
```

Excel dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import ExcelDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `sheet?` _int|str_ - number from 1 or name of an excel sheet
- `workbook_cache?` _dict_ - workbook cache
- `fill_merged_cells?` _bool_ - whether to fill merged cells
- `preserve_formatting?` _bool_ - whither to preserve formatting
- `adjust_floating_point_error?` _bool_ - whether to adjust floating point error
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**sheet**

```python
 | @Metadata.property
 | sheet()
```

Returns:

- `str|int` - sheet

**workbook\_cache**

```python
 | @Metadata.property
 | workbook_cache()
```

Returns:

- `dict` - workbook cache

**fill\_merged\_cells**

```python
 | @Metadata.property
 | fill_merged_cells()
```

Returns:

- `bool` - fill merged cells

**preserve\_formatting**

```python
 | @Metadata.property
 | preserve_formatting()
```

Returns:

- `bool` - preserve formatting

**adjust\_floating\_point\_error**

```python
 | @Metadata.property
 | adjust_floating_point_error()
```

Returns:

- `bool` - adjust floating point error

**expand**

```python
 | expand()
```

Expand metadata

### XlsxParser

```python
class XlsxParser(Parser)
```

XLSX parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import XlsxParser

### XlsParser

```python
class XlsParser(Parser)
```

XLS parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.excel import XlsParser

## frictionless.plugins.gsheets

### GsheetsPlugin

```python
class GsheetsPlugin(Plugin)
```

Plugin for Google Sheets

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheets import GsheetsPlugin`

### GsheetsDialect

```python
class GsheetsDialect(Dialect)
```

Gsheets dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheets import GsheetsDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**credentials**

```python
 | @Metadata.property
 | credentials()
```

Returns:

- `str` - credentials

### GsheetsParser

```python
class GsheetsParser(Parser)
```

Google Sheets parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.gsheets import GsheetsParser`

## frictionless.plugins.html

### HtmlPlugin

```python
class HtmlPlugin(Plugin)
```

Plugin for HTML

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlPlugin`

### HtmlDialect

```python
class HtmlDialect(Dialect)
```

Html dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `selector?` _str_ - HTML selector
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**selector**

```python
 | @Metadata.property
 | selector()
```

Returns:

- `str` - selector

**expand**

```python
 | expand()
```

Expand metadata

### HtmlParser

```python
class HtmlParser(Parser)
```

HTML parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.html import HtmlParser`

## frictionless.plugins.csv

### CsvPlugin

```python
class CsvPlugin(Plugin)
```

Plugin for Pandas

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.csv import CsvPlugin`

### CsvDialect

```python
class CsvDialect(Dialect)
```

Csv dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.csv import CsvDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `delimiter?` _str_ - csv delimiter
- `line_terminator?` _str_ - csv line terminator
- `quote_char?` _str_ - csv quote char
- `double_quote?` _bool_ - csv double quote
- `escape_char?` _str_ - csv escape char
- `null_sequence?` _str_ - csv null sequence
- `skip_initial_space?` _bool_ - csv skip initial space
- `comment_char?` _str_ - csv comment char
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**delimiter**

```python
 | @Metadata.property
 | delimiter()
```

Returns:

- `str` - delimiter

**line\_terminator**

```python
 | @Metadata.property
 | line_terminator()
```

Returns:

- `str` - line terminator

**quote\_char**

```python
 | @Metadata.property
 | quote_char()
```

Returns:

- `str` - quote char

**double\_quote**

```python
 | @Metadata.property
 | double_quote()
```

Returns:

- `bool` - double quote

**escape\_char**

```python
 | @Metadata.property
 | escape_char()
```

Returns:

- `str?` - escape char

**null\_sequence**

```python
 | @Metadata.property
 | null_sequence()
```

Returns:

- `str?` - null sequence

**skip\_initial\_space**

```python
 | @Metadata.property
 | skip_initial_space()
```

Returns:

- `bool` - if skipping initial space

**comment\_char**

```python
 | @Metadata.property
 | comment_char()
```

Returns:

- `str?` - comment char

**expand**

```python
 | expand()
```

Expand metadata

**to\_python**

```python
 | to_python()
```

Conver to Python's `csv.Dialect`

### CsvParser

```python
class CsvParser(Parser)
```

CSV parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.csv import CsvPlugins

## frictionless.plugins.sql

### SqlPlugin

```python
class SqlPlugin(Plugin)
```

Plugin for SQL

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlPlugin`

### SqlDialect

```python
class SqlDialect(Dialect)
```

SQL dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `table` _str_ - table
- `order_by?` _str_ - order_by
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### SqlParser

```python
class SqlParser(Parser)
```

SQL parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlParser`

### SqlStorage

```python
class SqlStorage(Storage)
```

SQL storage implementation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.sql import SqlStorage`

Arguments:

- `url?` _string_ - SQL connection string
- `engine?` _object_ - `sqlalchemy` engine
- `prefix?` _str_ - prefix for all tables
- `namespace?` _str_ - SQL scheme

## frictionless.plugins.ckan

### CkanPlugin

```python
class CkanPlugin(Plugin)
```

Plugin for CKAN

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ckan import CkanPlugin`

### CkanDialect

```python
class CkanDialect(Dialect)
```

Ckan dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ckan import CkanDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `resource?` _str_ - resource
- `dataset?` _str_ - dataset
- `apikey?` _str_ - apikey
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### CkanParser

```python
class CkanParser(Parser)
```

Ckan parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.ckan import CkanParser`

### CkanStorage

```python
class CkanStorage(Storage)
```

Ckan storage implementation

Arguments:

- `url` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dataset` _string_ - dataset id in CKAN e.g. "my-dataset"
- `apikey?` _str_ - API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
  
  
  API      | Usage
  -------- | --------
  Public   | `from frictionless.plugins.ckan import CkanStorage`

## frictionless.plugins.server

### ServerPlugin

```python
class ServerPlugin(Plugin)
```

Plugin for Server

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.server import ServerPlugin`

### ApiServer

```python
class ApiServer(Server)
```

API server implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.server import ApiParser`

## frictionless.plugins.json

### JsonPlugin

```python
class JsonPlugin(Plugin)
```

Plugin for Json

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonPlugin`

### JsonDialect

```python
class JsonDialect(Dialect)
```

Json dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `keys?` _str[]_ - a list of strings to use as data keys
- `keyed?` _bool_ - whether data rows are keyed
- `property?` _str_ - a path within JSON to the data
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**keys**

```python
 | @Metadata.property
 | keys()
```

Returns:

- `str[]?` - keys

**keyed**

```python
 | @Metadata.property
 | keyed()
```

Returns:

- `bool` - keyed

**property**

```python
 | @Metadata.property
 | property()
```

Returns:

- `str?` - property

**expand**

```python
 | expand()
```

Expand metadata

### JsonParser

```python
class JsonParser(Parser)
```

JSON parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonParser

### JsonlParser

```python
class JsonlParser(Parser)
```

JSONL parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.json import JsonlParser

## frictionless.plugins.inline

### InlinePlugin

```python
class InlinePlugin(Plugin)
```

Plugin for Inline

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.inline import InlinePlugin`

### InlineDialect

```python
class InlineDialect(Dialect)
```

Inline dialect representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.inline import InlineDialect`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `keys?` _str[]_ - a list of strings to use as data keys
- `keyed?` _bool_ - whether data rows are keyed
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**keys**

```python
 | @Metadata.property
 | keys()
```

Returns:

- `str[]?` - keys

**keyed**

```python
 | @Metadata.property
 | keyed()
```

Returns:

- `bool` - keyed

**expand**

```python
 | expand()
```

Expand metadata

### InlineParser

```python
class InlineParser(Parser)
```

Inline parser implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.inline import InlineParser

## frictionless.plugins.multipart

### MultipartPlugin

```python
class MultipartPlugin(Plugin)
```

Plugin for Multipart Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.multipart import MultipartPlugin`

### MultipartControl

```python
class MultipartControl(Control)
```

Multipart control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.multipart import MultipartControl`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**expand**

```python
 | expand()
```

Expand metadata

### MultipartLoader

```python
class MultipartLoader(Loader)
```

Multipart loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.multipart import MultipartLoader`

## frictionless.plugins.text

### TextPlugin

```python
class TextPlugin(Plugin)
```

Plugin for Text Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import TextPlugin`

### TextControl

```python
class TextControl(Control)
```

Text control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.text import TextControl`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### TextLoader

```python
class TextLoader(Loader)
```

Text loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.text import TextLoader`

## frictionless.plugins.local

### LocalPlugin

```python
class LocalPlugin(Plugin)
```

Plugin for Local Data

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import LocalPlugin`

### LocalControl

```python
class LocalControl(Control)
```

Local control representation

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import LocalControl`

Arguments:

- `descriptor?` _str|dict_ - descriptor
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### LocalLoader

```python
class LocalLoader(Loader)
```

Local loader implementation.

API      | Usage
-------- | --------
Public   | `from frictionless.plugins.local import LocalLoader`

## frictionless.control

### Control

```python
class Control(Metadata)
```

Control representation

API      | Usage
-------- | --------
Public   | `from frictionless import Control`

Arguments:

- `descriptor?` _str|dict_ - descriptor
- `newline?` _str_ - a string to be used for `io.open(..., newline=newline)`
- `detectEncoding?` _func_ - a function to detect encoding `(sample) -> encoding`
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**newline**

```python
 | @Metadata.property
 | newline()
```

Returns:

- `str` - a string to be used for `io.open(..., newline=newline)`

**detect\_encoding**

```python
 | @Metadata.property
 | detect_encoding()
```

Returns:

- `func` - detect encoding function

## frictionless.extract

## frictionless.extract.main

**extract**

```python
extract(source, *, type=None, process=None, stream=False, **options)
```

Extract resource rows

API      | Usage
-------- | --------
Public   | `from frictionless import extract`

Arguments:

- `source` _dict|str_ - data source
- `type` _str_ - source type - package of resource (default: infer)
- `process?` _func_ - a row processor function
- `stream?` _bool_ - return a row stream(s) instead of loading into memory
- `**options` _dict_ - options for the underlaying function
  

Returns:

- `Row[]|{path` - Row[]}: rows in a form depending on the source type

## frictionless.extract.package

**extract\_package**

```python
extract_package(source, *, process=None, stream=False, **options)
```

Extract package rows

API      | Usage
-------- | --------
Public   | `from frictionless import extract_package`

Arguments:

- `source` _dict|str_ - data resource descriptor
- `process?` _func_ - a row processor function
- `stream?` _bool_ - return a row streams instead of loading into memory
- `**options` _dict_ - Package constructor options
  

Returns:

- `{path` - Row[]}: a dictionary of arrays/streams of rows

## frictionless.extract.resource

**extract\_resource**

```python
extract_resource(source, *, process=None, stream=False, **options)
```

Extract resource rows

API      | Usage
-------- | --------
Public   | `from frictionless import extract_resource`

Arguments:

- `source` _dict|str_ - data resource descriptor
- `process?` _func_ - a row processor function
- `**options` _dict_ - Resource constructor options
  

Returns:

- `Row[]` - an array/stream of rows

## frictionless.errors

### Error

```python
class Error(Metadata)
```

Error representation

API      | Usage
-------- | --------
Public   | `from frictionless import errors`

Arguments:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**note**

```python
 | @property
 | note()
```

Returns:

- `str` - note

**message**

```python
 | @property
 | message()
```

Returns:

- `str` - message

### HeaderError

```python
class HeaderError(Error)
```

Header error representation

Arguments:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `labels` _str[]_ - header labels
- `label` _str_ - an errored label
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### LabelError

```python
class LabelError(HeaderError)
```

Label error representation

Arguments:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `labels` _str[]_ - header labels
- `label` _str_ - an errored label
- `field_name` _str_ - field name
- `field_number` _int_ - field number
- `field_position` _int_ - field position
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

### RowError

```python
class RowError(Error)
```

Row error representation

Arguments:

- `descriptor?` _str|dict_ - error descriptor
- `note` _str_ - an error note
- `row_number` _int_ - row number
- `row_position` _int_ - row position
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**from\_row**

```python
 | @classmethod
 | from_row(cls, row, *, note)
```

Create an error from a row

Arguments:

- `row` _Row_ - row
- `note` _str_ - note
  

Returns:

- `RowError` - error

### CellError

```python
class CellError(RowError)
```

Cell error representation

Arguments:

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

**from\_row**

```python
 | @classmethod
 | from_row(cls, row, *, note, field_name)
```

Create and error from a cell

Arguments:

- `row` _Row_ - row
- `note` _str_ - note
- `field_name` _str_ - field name
  

Returns:

- `CellError` - error

## frictionless.describe

## frictionless.describe.main

**describe**

```python
describe(source, *, type=None, **options)
```

Describe the data source

API      | Usage
-------- | --------
Public   | `from frictionless import describe`

Arguments:

- `source` _any_ - data source
- `type` _str_ - source type - `schema`, `resource` or `package` (default: infer)
- `**options` _dict_ - options for the underlaying describe function
  

Returns:

- `Package|Resource|Schema` - metadata

## frictionless.describe.package

**describe\_package**

```python
describe_package(source, *, expand=False, nostats=False, **options)
```

Describe the given source as a package

API      | Usage
-------- | --------
Public   | `from frictionless import describe_package`

Arguments:

- `source` _any_ - data source
- `expand?` _bool_ - if `True` it will expand the metadata
- `nostats?` _bool_ - if `True` it not infer resource's stats
- `**options` _dict_ - Package constructor options
  

Returns:

- `Package` - data package

## frictionless.describe.schema

**describe\_schema**

```python
describe_schema(source, *, expand=False, **options)
```

Describe the given source as a schema

API      | Usage
-------- | --------
Public   | `from frictionless import describe_schema`

Arguments:

- `source` _any_ - data source
- `expand?` _bool_ - if `True` it will expand the metadata
- `**options` _dict_ - Resource constructor options
  

Returns:

- `Schema` - table schema

## frictionless.describe.resource

**describe\_resource**

```python
describe_resource(source, *, expand=False, nostats=False, **options)
```

Describe the given source as a resource

API      | Usage
-------- | --------
Public   | `from frictionless import describe_resource`

Arguments:

- `source` _any_ - data source
- `expand?` _bool_ - if `True` it will expand the metadata
- `nostats?` _bool_ - if `True` it not infer resource's stats
- `**options` _dict_ - Resource constructor options
  

Returns:

- `Resource` - data resource

## frictionless.schema

### Schema

```python
class Schema(Metadata)
```

Schema representation

API      | Usage
-------- | --------
Public   | `from frictionless import Schema`

Arguments:

- `descriptor?` _str|dict_ - schema descriptor
- `fields?` _dict[]_ - list of field descriptors
- `missing_values?` _str[]_ - missing values
- `primary_key?` _str[]_ - primary key
- `foreign_keys?` _dict[]_ - foreign keys
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**missing\_values**

```python
 | @Metadata.property
 | missing_values()
```

Returns:

- `str[]` - missing values

**primary\_key**

```python
 | @Metadata.property
 | primary_key()
```

Returns:

- `str[]` - primary key field names

**foreign\_keys**

```python
 | @Metadata.property
 | foreign_keys()
```

Returns:

- `dict[]` - foreign keys

**fields**

```python
 | @Metadata.property
 | fields()
```

Returns:

- `Field[]` - an array of field instances

**field\_names**

```python
 | @Metadata.property(cache=False, write=False)
 | field_names()
```

Returns:

- `str[]` - an array of field names

**add\_field**

```python
 | add_field(descriptor)
```

Add new field to schema.

The schema descriptor will be validated with newly added field descriptor.

Arguments:

- `descriptor` _dict_ - field descriptor
  

Returns:

- `Field/None` - added `Field` instance or `None` if not added

**get\_field**

```python
 | get_field(name)
```

Get schema's field by name.

Arguments:

- `name` _str_ - schema field name
  

Raises:

- `FrictionlessException` - if field is not found
  

Returns:

- `Field` - `Field` instance or `None` if not found

**has\_field**

```python
 | has_field(name)
```

Check if a field is present

Arguments:

- `name` _str_ - schema field name
  

Returns:

- `bool` - whether there is the field

**remove\_field**

```python
 | remove_field(name)
```

Remove field by name.

The schema descriptor will be validated after field descriptor removal.

Arguments:

- `name` _str_ - schema field name
  

Raises:

- `FrictionlessException` - if field is not found
  

Returns:

- `Field/None` - removed `Field` instances or `None` if not found

**expand**

```python
 | expand()
```

Expand the schema

**read\_cells**

```python
 | read_cells(cells)
```

Read a list of cells (normalize/cast)

Arguments:

- `cells` _any[]_ - list of cells
  

Returns:

- `any[]` - list of processed cells

**write\_cells**

```python
 | write_cells(cells, *, types=[])
```

Write a list of cells (normalize/uncast)

Arguments:

- `cells` _any[]_ - list of cells
  

Returns:

- `any[]` - list of processed cells

**from\_sample**

```python
 | @staticmethod
 | from_sample(sample, *, type=None, names=None, confidence=config.DEFAULT_INFER_CONFIDENCE, float_numbers=config.DEFAULT_FLOAT_NUMBER, missing_values=config.DEFAULT_MISSING_VALUES)
```

Infer schema from sample

Arguments:

- `sample` _any[][]_ - data sample
- `type?` _str_ - enforce all the field to be the given type
- `names` _str[]_ - enforce field names
- `confidence` _float_ - infer confidence from 0 to 1
- `float_numbers` _bool_ - infer numbers as `float` instead of `Decimal`
- `missing_values` _str[]_ - provide custom missing values
  

Returns:

- `Schema` - schema

## frictionless.check

### Check

```python
class Check(Metadata)
```

Check representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Checks`

It's an interface for writing Frictionless checks.

Arguments:

- `descriptor?` _str|dict_ - schema descriptor
  

Raises:

- `FrictionlessException` - raise if metadata is invalid

**table**

```python
 | @property
 | table()
```

Returns:

- `Table?` - table object available after the `check.connect` call

**connect**

```python
 | connect(table)
```

Connect to the given table

Arguments:

- `table` _Table_ - data table

**prepare**

```python
 | prepare()
```

Called before validation

**validate\_task**

```python
 | validate_task()
```

Called to validate the check itself

**Yields**:

- `Error` - found errors

**validate\_schema**

```python
 | validate_schema(schema)
```

Called to validate the given schema

Arguments:

- `schema` _Schema_ - table schema
  

**Yields**:

- `Error` - found errors

**validate\_header**

```python
 | validate_header(header)
```

Called to validate the given header

Arguments:

- `header` _Header_ - table header
  

**Yields**:

- `Error` - found errors

**validate\_row**

```python
 | validate_row(row)
```

Called to validate the given row (on every row)

Arguments:

- `row` _Row_ - table row
  

**Yields**:

- `Error` - found errors

**validate\_table**

```python
 | validate_table()
```

Called to validate the table (after no rows left)

**Yields**:

- `Error` - found errors

## frictionless.resource

### Resource

```python
class Resource(Metadata)
```

Resource representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Resource`

Arguments:

- `descriptor?` _str|dict_ - resource descriptor
- `name?` _str_ - resource name (for machines)
- `title?` _str_ - resource title (for humans)
- `descriptor?` _str_ - resource descriptor
- `licenses?` _dict[]_ - resource licenses
- `sources?` _dict[]_ - resource sources
- `path?` _str_ - file path
- `data?` _any[][]_ - array or data arrays
- `scheme?` _str_ - file scheme
- `format?` _str_ - file format
- `hashing?` _str_ - file hashing
- `encoding?` _str_ - file encoding
- `innerpath?` _str_ - file compression path
- `compression?` _str_ - file compression
- `control?` _dict_ - file control
- `dialect?` _dict_ - table dialect
- `layout?` _dict_ - table layout
- `schema?` _dict_ - table schema
- `stats?` _dict_ - table stats
- `profile?` _str_ - resource profile
- `basepath?` _str_ - resource basepath
- `onerror?` _ignore|warn|raise_ - behaviour if there is an error
- `trusted?` _bool_ - don't raise an exception on unsafe paths
- `package?` _Package_ - resource package
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**name**

```python
 | @Metadata.property
 | name()
```

Returns
    str: resource name

**title**

```python
 | @Metadata.property
 | title()
```

Returns
    str: resource title

**description**

```python
 | @Metadata.property
 | description()
```

Returns
    str: resource description

**licenses**

```python
 | @Metadata.property
 | licenses()
```

Returns
    dict[]: resource licenses

**sources**

```python
 | @Metadata.property
 | sources()
```

Returns
    dict[]: resource sources

**profile**

```python
 | @Metadata.property
 | profile()
```

Returns
    str?: resource profile

**path**

```python
 | @Metadata.property
 | path()
```

Returns
    str?: resource path

**data**

```python
 | @Metadata.property
 | data()
```

Returns
    any[][]?: resource data

**scheme**

```python
 | @Metadata.property
 | scheme()
```

Returns
    str?: resource scheme

**format**

```python
 | @Metadata.property
 | format()
```

Returns
    str?: resource format

**hashing**

```python
 | @Metadata.property
 | hashing()
```

Returns
    str?: resource hashing

**encoding**

```python
 | @Metadata.property
 | encoding()
```

Returns
    str?: resource encoding

**innerpath**

```python
 | @Metadata.property
 | innerpath()
```

Returns
    str?: resource compression path

**compression**

```python
 | @Metadata.property
 | compression()
```

Returns
    str?: resource compression

**control**

```python
 | @Metadata.property
 | control()
```

Returns
    Control?: resource control

**dialect**

```python
 | @Metadata.property
 | dialect()
```

Returns
    Dialect?: resource dialect

**layout**

```python
 | @Metadata.property
 | layout()
```

Returns:

- `Layout?` - table layout

**schema**

```python
 | @Metadata.property
 | schema()
```

Returns
    Schema: resource schema

**sample**

```python
 | @property
 | sample()
```

Tables's rows used as sample.

These sample rows are used internally to infer characteristics of the
source file (e.g. schema, ...).

Returns:

- `list[]?` - table sample

**header**

```python
 | @property
 | header()
```

Returns:

- `str[]?` - table header

**lookup**

```python
 | @property
 | lookup()
```

Returns:

- `any?` - table lookup

**stats**

```python
 | @Metadata.property
 | stats()
```

Returns
    dict?: resource stats

**basepath**

```python
 | @Metadata.property(cache=False, write=False)
 | basepath()
```

Returns
    str: resource basepath

**fullpath**

```python
 | @Metadata.property(cache=False, write=False)
 | fullpath()
```

Returns
    str: resource fullpath

**onerror**

```python
 | @Metadata.property(cache=False, write=False)
 | onerror()
```

Returns:

- `ignore|warn|raise` - on error bahaviour

**trusted**

```python
 | @Metadata.property(cache=False, write=False)
 | trusted()
```

Returns:

- `bool` - don't raise an exception on unsafe paths

**package**

```python
 | @Metadata.property(cache=False, write=False)
 | package()
```

Returns:

- `Package?` - parent package

**memory**

```python
 | @Metadata.property(write=False)
 | memory()
```

Returns
    bool: if resource is memory

**remote**

```python
 | @Metadata.property(write=False)
 | remote()
```

Returns
    bool: if resource is remote

**multipart**

```python
 | @Metadata.property(write=False)
 | multipart()
```

Returns
    bool: if resource is multipart

**tabular**

```python
 | @Metadata.property(write=False)
 | tabular()
```

Returns
    bool: if resource is tabular

**byte\_stream**

```python
 | @property
 | byte_stream()
```

Byte stream in form of a generator

**Yields**:

- `gen<bytes>?` - byte stream

**text\_stream**

```python
 | @property
 | text_stream()
```

Text stream in form of a generator

**Yields**:

- `gen<str[]>?` - data stream

**data\_stream**

```python
 | @property
 | data_stream()
```

Data stream in form of a generator

**Yields**:

- `gen<any[][]>?` - data stream

**row\_stream**

```python
 | @property
 | row_stream()
```

Row stream in form of a generator of Row objects

**Yields**:

- `gen<Row[]>?` - row stream

**expand**

```python
 | expand()
```

Expand metadata

**infer**

```python
 | infer(*, stats=False)
```

Infer metadata

Arguments:

- `stats?` _bool_ - stream file completely and infer stats

**open**

```python
 | open()
```

Open the resource as "io.open" does

Raises:

- `FrictionlessException` - any exception that occurs

**close**

```python
 | close()
```

Close the table as "filelike.close" does

**closed**

```python
 | @property
 | closed()
```

Whether the table is closed

Returns:

- `bool` - if closed

**read\_bytes**

```python
 | read_bytes()
```

Read data into memory

Returns:

- `any[][]` - table data

**read\_text**

```python
 | read_text()
```

Read text into memory

Returns:

- `str` - table data

**read\_data**

```python
 | read_data()
```

Read data into memory

Returns:

- `any[][]` - table data

**read\_rows**

```python
 | read_rows()
```

Read rows into memory

Returns:

- `Row[]` - table rows

**write**

```python
 | write(target)
```

Write this resource to the target resource

Arguments:

- `target` _Resource_ - target Resource

**from\_petl**

```python
 | @staticmethod
 | from_petl(storage, *, view, **options)
```

Create a resource from PETL container

**from\_storage**

```python
 | @staticmethod
 | from_storage(storage, *, name)
```

Import resource from storage

Arguments:

- `storage` _Storage_ - storage instance
- `name` _str_ - resource name

**from\_ckan**

```python
 | @staticmethod
 | from_ckan(*, name, url, dataset, apikey=None)
```

Import resource from CKAN

Arguments:

- `name` _string_ - resource name
- `url` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dataset` _string_ - dataset id in CKAN e.g. "my-dataset"
- `apikey?` _str_ - API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"

**from\_sql**

```python
 | @staticmethod
 | from_sql(*, name, url=None, engine=None, prefix="", namespace=None)
```

Import resource from SQL table

Arguments:

- `name` _str_ - resource name
- `url?` _string_ - SQL connection string
- `engine?` _object_ - `sqlalchemy` engine
- `prefix?` _str_ - prefix for all tables
- `namespace?` _str_ - SQL scheme

**from\_pandas**

```python
 | @staticmethod
 | from_pandas(dataframe)
```

Import resource from Pandas dataframe

Arguments:

- `dataframe` _str_ - padas dataframe

**from\_spss**

```python
 | @staticmethod
 | from_spss(*, name, basepath)
```

Import resource from SPSS file

Arguments:

- `name` _str_ - resource name
- `basepath` _str_ - SPSS dir path

**from\_bigquery**

```python
 | @staticmethod
 | from_bigquery(*, name, service, project, dataset, prefix="")
```

Import resource from BigQuery table

Arguments:

- `name` _str_ - resource name
- `service` _object_ - BigQuery `Service` object
- `project` _str_ - BigQuery project name
- `dataset` _str_ - BigQuery dataset name
- `prefix?` _str_ - prefix for all names

**to\_copy**

```python
 | to_copy(**options)
```

Create a copy of the resource

**to\_storage**

```python
 | to_storage(storage, *, force=False)
```

Export resource to storage

Arguments:

- `storage` _Storage_ - storage instance
- `force` _bool_ - overwrite existent

**to\_ckan**

```python
 | to_ckan(*, url, dataset, apikey=None, force=False)
```

Export resource to CKAN

Arguments:

- `url` _string_ - CKAN instance url e.g. "https://demo.ckan.org"
- `dataset` _string_ - dataset id in CKAN e.g. "my-dataset"
- `apikey?` _str_ - API key for CKAN e.g. "51912f57-a657-4caa-b2a7-0a1c16821f4b"
- `force` _bool_ - (optional) overwrite existing data

**to\_sql**

```python
 | to_sql(*, url=None, engine=None, prefix="", namespace=None, force=False)
```

Export resource to SQL table

Arguments:

- `url?` _string_ - SQL connection string
- `engine?` _object_ - `sqlalchemy` engine
- `prefix?` _str_ - prefix for all tables
- `namespace?` _str_ - SQL scheme
- `force?` _bool_ - overwrite existent

**to\_pandas**

```python
 | to_pandas()
```

Export resource to Pandas dataframe

Arguments:

- `dataframes` _dict_ - pandas dataframes
- `force` _bool_ - overwrite existent

**to\_spss**

```python
 | to_spss(*, basepath, force=False)
```

Export resource to SPSS file

Arguments:

- `basepath` _str_ - SPSS dir path
- `force` _bool_ - overwrite existent

**to\_bigquery**

```python
 | to_bigquery(*, service, project, dataset, prefix="", force=False)
```

Export resource to Bigquery table

Arguments:

- `service` _object_ - BigQuery `Service` object
- `project` _str_ - BigQuery project name
- `dataset` _str_ - BigQuery dataset name
- `prefix?` _str_ - prefix for all names
- `force` _bool_ - overwrite existent

## frictionless.dialect

## frictionless.transform

## frictionless.transform.main

**transform**

```python
transform(source, type=None, **options)
```

Transform resource

API      | Usage
-------- | --------
Public   | `from frictionless import transform`

Arguments:

- `source` _any_ - data source
- `type` _str_ - source type - package, resource or pipeline (default: infer)
- `**options` _dict_ - options for the underlaying function
  

Returns:

- `any` - the transform result

## frictionless.transform.pipeline

**transform\_pipeline**

```python
transform_pipeline(source, *, parallel=False, **options)
```

Transform package

API      | Usage
-------- | --------
Public   | `from frictionless import transform_package`

Arguments:

- `source` _any_ - a pipeline descriptor
- `**options` _dict_ - Pipeline constructor options
  

Returns:

- `any` - the pipeline output

## frictionless.transform.package

**transform\_package**

```python
transform_package(source, *, steps, **options)
```

Transform package

API      | Usage
-------- | --------
Public   | `from frictionless import transform_package`

Arguments:

- `source` _any_ - data source
- `steps` _Step[]_ - transform steps
- `**options` _dict_ - Package constructor options
  

Returns:

- `Package` - the transform result

## frictionless.transform.resource

**transform\_resource**

```python
transform_resource(source, *, steps, **options)
```

Transform resource

API      | Usage
-------- | --------
Public   | `from frictionless import transform_resource`

Arguments:

- `source` _any_ - data source
- `steps` _Step[]_ - transform steps
- `**options` _dict_ - Package constructor options
  

Returns:

- `Resource` - the transform result

## frictionless.parser

### Parser

```python
class Parser()
```

Parser representation

API      | Usage
-------- | --------
Public   | `from frictionless import Parser`

Arguments:

- `resource` _Resource_ - resource

**resource**

```python
 | @property
 | resource()
```

Returns:

- `Resource` - resource

**loader**

```python
 | @property
 | loader()
```

Returns:

- `Loader` - loader

**data\_stream**

```python
 | @property
 | data_stream()
```

**Yields**:

- `any[][]` - data stream

**open**

```python
 | open()
```

Open the parser as "io.open" does

**close**

```python
 | close()
```

Close the parser as "filelike.close" does

**closed**

```python
 | @property
 | closed()
```

Whether the parser is closed

Returns:

- `bool` - if closed

**read\_loader**

```python
 | read_loader()
```

Create and open loader

Returns:

- `Loader` - loader

**read\_data\_stream**

```python
 | read_data_stream()
```

Read data stream

Returns:

- `gen<any[][]>` - data stream

**read\_data\_stream\_create**

```python
 | read_data_stream_create(loader)
```

Create data stream from loader

Arguments:

- `loader` _Loader_ - loader
  

Returns:

- `gen<any[][]>` - data stream

**read\_data\_stream\_handle\_errors**

```python
 | read_data_stream_handle_errors(data_stream)
```

Wrap data stream into error handler

Arguments:

- `gen<any[][]>` - data stream
  

Returns:

- `gen<any[][]>` - data stream

**write\_row\_stream**

```python
 | write_row_stream(read_row_stream)
```

Write row stream into the resource

Arguments:

- `read_row_stream` _gen<Row[]>_ - row stream factory

## frictionless.report

### Report

```python
class Report(Metadata)
```

Report representation.

API      | Usage
-------- | --------
Public   | `from frictionless import Report`

Arguments:

- `descriptor?` _str|dict_ - report descriptor
- `time` _float_ - validation time
- `errors` _Error[]_ - validation errors
- `tasks` _ReportTask[]_ - validation tasks
  

Raises:

- `FrictionlessException` - raise any error that occurs during the process

**version**

```python
 | @property
 | version()
```

Returns:

- `str` - frictionless version

**time**

```python
 | @property
 | time()
```

Returns:

- `float` - validation time

**valid**

```python
 | @property
 | valid()
```

Returns:

- `bool` - validation result

**stats**

```python
 | @property
 | stats()
```

Returns:

- `dict` - validation stats

**errors**

```python
 | @property
 | errors()
```

Returns:

- `Error[]` - validation errors

**tasks**

```python
 | @property
 | tasks()
```

Returns:

- `ReportTask[]` - validation tasks

**task**

```python
 | @property
 | task()
```

Returns:

- `ReportTask` - validation task (if there is only one)
  

Raises:

- `FrictionlessException` - if there are more that 1 task

**expand**

```python
 | expand()
```

Expand metadata

**flatten**

```python
 | flatten(spec)
```

Flatten the report

Parameters
spec (any[]): flatten specification

Returns:

- `any[]` - flatten report

**from\_validate**

```python
 | @staticmethod
 | from_validate(validate)
```

Validate function wrapper

Arguments:

- `validate` _func_ - validate
  

Returns:

- `func` - wrapped validate

### ReportTask

```python
class ReportTask(Metadata)
```

Report task representation.

API      | Usage
-------- | --------
Public   | `from frictionless import ReportTask`

Arguments:

- `descriptor?` _str|dict_ - schema descriptor
- `time` _float_ - validation time
- `scope` _str[]_ - validation scope
- `partial` _bool_ - wehter validation was partial
- `errors` _Error[]_ - validation errors
- `task` _Task_ - validation task
  
  # Raises
- `FrictionlessException` - raise any error that occurs during the process

**resource**

```python
 | @property
 | resource()
```

Returns:

- `Resource` - resource

**time**

```python
 | @property
 | time()
```

Returns:

- `float` - validation time

**valid**

```python
 | @property
 | valid()
```

Returns:

- `bool` - validation result

**scope**

```python
 | @property
 | scope()
```

Returns:

- `str[]` - validation scope

**partial**

```python
 | @property
 | partial()
```

Returns:

- `bool` - if validation partial

**stats**

```python
 | @property
 | stats()
```

Returns:

- `dict` - validation stats

**errors**

```python
 | @property
 | errors()
```

Returns:

- `Error[]` - validation errors

**error**

```python
 | @property
 | error()
```

Returns:

- `Error` - validation error if there is only one
  

Raises:

- `FrictionlessException` - if more than one errors

**expand**

```python
 | expand()
```

Expand metadata

**flatten**

```python
 | flatten(spec)
```

Flatten the report

Parameters
spec (any[]): flatten specification

Returns:

- `any[]` - flatten task report

## frictionless.layout

### Layout

```python
class Layout(Metadata)
```

Layout representation

API      | Usage
-------- | --------
Public   | `from frictionless import Layout`

Arguments:

- `descriptor?` _str|dict_ - layout descriptor
  pick_fields? ((str|int)[]): what fields to pick
  skip_fields? ((str|int)[]): what fields to skip
- `limit_fields?` _int_ - amount of fields
- `offset_fields?` _int_ - from what field to start
  pick_rows? ((str|int)[]): what rows to pick
  skip_rows? ((str|int)[]): what rows to skip
- `limit_rows?` _int_ - amount of rows
- `offset_rows?` _int_ - from what row to start

**header**

```python
 | @Metadata.property
 | header()
```

Returns:

- `bool` - if there is a header row

**header\_rows**

```python
 | @Metadata.property
 | header_rows()
```

Returns:

- `int[]` - header rows

**header\_join**

```python
 | @Metadata.property
 | header_join()
```

Returns:

- `str` - header joiner

**header\_case**

```python
 | @Metadata.property
 | header_case()
```

Returns:

- `str` - header case sensitive

**pick\_fields**

```python
 | @Metadata.property
 | pick_fields()
```

Returns:

- `(str|int)[]?` - pick fields

**skip\_fields**

```python
 | @Metadata.property
 | skip_fields()
```

Returns:

- `(str|int)[]?` - skip fields

**limit\_fields**

```python
 | @Metadata.property
 | limit_fields()
```

Returns:

- `int?` - limit fields

**offset\_fields**

```python
 | @Metadata.property
 | offset_fields()
```

Returns:

- `int?` - offset fields

**pick\_rows**

```python
 | @Metadata.property
 | pick_rows()
```

Returns:

- `(str|int)[]?` - pick rows

**skip\_rows**

```python
 | @Metadata.property
 | skip_rows()
```

Returns:

- `(str|int)[]?` - skip rows

**limit\_rows**

```python
 | @Metadata.property
 | limit_rows()
```

Returns:

- `int?` - limit rows

**offset\_rows**

```python
 | @Metadata.property
 | offset_rows()
```

Returns:

- `int?` - offset rows

**is\_field\_filtering**

```python
 | @Metadata.property(write=False)
 | is_field_filtering()
```

Returns:

- `bool` - whether there is a field filtering

**pick\_fields\_compiled**

```python
 | @Metadata.property(write=False)
 | pick_fields_compiled()
```

Returns:

- `re?` - compiled pick fields

**skip\_fields\_compiled**

```python
 | @Metadata.property(write=False)
 | skip_fields_compiled()
```

Returns:

- `re?` - compiled skip fields

**pick\_rows\_compiled**

```python
 | @Metadata.property(write=False)
 | pick_rows_compiled()
```

Returns:

- `re?` - compiled pick rows

**skip\_rows\_compiled**

```python
 | @Metadata.property(write=False)
 | skip_rows_compiled()
```

Returns:

- `re?` - compiled skip fields

**expand**

```python
 | expand()
```

Expand metadata

## frictionless.step

## frictionless.\_\_main\_\_

## frictionless.server

### Server

```python
class Server()
```

Server representation

API      | Usage
-------- | --------
Public   | `from frictionless import Schema`

**start**

```python
 | start(port)
```

Start the server

Arguments:

- `port` _int_ - HTTP port

**stop**

```python
 | stop()
```

Stop the server

## frictionless.exception

### FrictionlessException

```python
class FrictionlessException(Exception)
```

Main Frictionless exception

API      | Usage
-------- | --------
Public   | `from frictionless import FrictionlessException`

Arguments:

- `error` _Error_ - an underlaying error

**error**

```python
 | @property
 | error()
```

Returns:

- `Error` - error

## frictionless.types

## frictionless.types.yearmonth

### YearmonthType

```python
class YearmonthType(Type)
```

Yearmonth type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.datetime

### DatetimeType

```python
class DatetimeType(Type)
```

Datetime type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.date

### DateType

```python
class DateType(Type)
```

Date type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.string

### StringType

```python
class StringType(Type)
```

String type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.object

### ObjectType

```python
class ObjectType(Type)
```

Object type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.geojson

### GeojsonType

```python
class GeojsonType(Type)
```

Geojson type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.year

### YearType

```python
class YearType(Type)
```

Year type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.integer

### IntegerType

```python
class IntegerType(Type)
```

Integer type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.time

### TimeType

```python
class TimeType(Type)
```

Time type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.geopoint

### GeopointType

```python
class GeopointType(Type)
```

Geopoint type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.array

### ArrayType

```python
class ArrayType(Type)
```

Array type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.boolean

### BooleanType

```python
class BooleanType(Type)
```

Boolean type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.any

### AnyType

```python
class AnyType(Type)
```

Any type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.duration

### DurationType

```python
class DurationType(Type)
```

Duration type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.types.number

### NumberType

```python
class NumberType(Type)
```

Number type implementation.

API      | Usage
-------- | --------
Public   | `from frictionless import types`

## frictionless.loader

### Loader

```python
class Loader()
```

Loader representation

API      | Usage
-------- | --------
Public   | `from frictionless import Loader`

Arguments:

- `resource` _Resource_ - resource

**resource**

```python
 | @property
 | resource()
```

Returns:

- `resource` _Resource_ - resource

**byte\_stream**

```python
 | @property
 | byte_stream()
```

Resource byte stream

The stream is available after opening the loader

Returns:

- `io.ByteStream` - resource byte stream

**text\_stream**

```python
 | @property
 | text_stream()
```

Resource text stream

The stream is available after opening the loader

Returns:

- `io.TextStream` - resource text stream

**open**

```python
 | open()
```

Open the loader as "io.open" does

**close**

```python
 | close()
```

Close the loader as "filelike.close" does

**closed**

```python
 | @property
 | closed()
```

Whether the loader is closed

Returns:

- `bool` - if closed

**read\_byte\_stream**

```python
 | read_byte_stream()
```

Read bytes stream

Returns:

- `io.ByteStream` - resource byte stream

**read\_byte\_stream\_create**

```python
 | read_byte_stream_create()
```

Create bytes stream

Returns:

- `io.ByteStream` - resource byte stream

**read\_byte\_stream\_infer\_stats**

```python
 | read_byte_stream_infer_stats(byte_stream)
```

Infer byte stream stats

Arguments:

- `byte_stream` _io.ByteStream_ - resource byte stream
  

Returns:

- `io.ByteStream` - resource byte stream

**read\_byte\_stream\_decompress**

```python
 | read_byte_stream_decompress(byte_stream)
```

Decompress byte stream

Arguments:

- `byte_stream` _io.ByteStream_ - resource byte stream
  

Returns:

- `io.ByteStream` - resource byte stream

**read\_text\_stream**

```python
 | read_text_stream()
```

Read text stream

Returns:

- `io.TextStream` - resource text stream

**read\_text\_stream\_infer\_encoding**

```python
 | read_text_stream_infer_encoding(byte_stream)
```

Infer text stream encoding

Arguments:

- `byte_stream` _io.ByteStream_ - resource byte stream

**read\_text\_stream\_decode**

```python
 | read_text_stream_decode(byte_stream)
```

Decode text stream

Arguments:

- `byte_stream` _io.ByteStream_ - resource byte stream
  

Returns:

- `text_stream` _io.TextStream_ - resource text stream

**write\_byte\_stream**

```python
 | write_byte_stream(path)
```

Write from a temporary file

Arguments:

- `path` _str_ - path to a temporary file
  

Returns:

- `any` - result of writing e.g. resulting path

**write\_byte\_stream\_create**

```python
 | write_byte_stream_create(path)
```

Create byte stream for writing

Arguments:

- `path` _str_ - path to a temporary file
  

Returns:

- `io.ByteStream` - byte stream

**write\_byte\_stream\_save**

```python
 | write_byte_stream_save(byte_stream)
```

Store byte stream

## frictionless.validate

## frictionless.validate.main

**validate**

```python
@Report.from_validate
validate(source, type=None, **options)
```

Validate resource

API      | Usage
-------- | --------
Public   | `from frictionless import validate`

Arguments:

- `source` _dict|str_ - a data source
- `type` _str_ - source type - inquiry, package, resource, schema or table
- `**options` _dict_ - options for the underlaying function
  

Returns:

- `Report` - validation report

## frictionless.validate.package

**validate\_package**

```python
@Report.from_validate
validate_package(source, noinfer=False, nolookup=False, parallel=False, **options)
```

Validate package

API      | Usage
-------- | --------
Public   | `from frictionless import validate_package`

Arguments:

- `source` _dict|str_ - a package descriptor
- `basepath?` _str_ - package basepath
- `trusted?` _bool_ - don't raise an exception on unsafe paths
- `noinfer?` _bool_ - don't call `package.infer`
- `nolookup?` _bool_ - don't read lookup tables skipping integrity checks
- `parallel?` _bool_ - enable multiprocessing
- `**options` _dict_ - Package constructor options
  

Returns:

- `Report` - validation report

## frictionless.validate.inquiry

**validate\_inquiry**

```python
@Report.from_validate
validate_inquiry(source, *, parallel=False, **options)
```

Validate inquiry

API      | Usage
-------- | --------
Public   | `from frictionless import validate_inquiry`

Arguments:

- `source` _dict|str_ - an inquiry descriptor
- `parallel?` _bool_ - enable multiprocessing
  

Returns:

- `Report` - validation report

## frictionless.validate.schema

**validate\_schema**

```python
@Report.from_validate
validate_schema(source, **options)
```

Validate schema

API      | Usage
-------- | --------
Public   | `from frictionless import validate_schema`

Arguments:

- `source` _dict|str_ - a schema descriptor
  

Returns:

- `Report` - validation report

## frictionless.validate.resource

**validate\_resource**

```python
@Report.from_validate
validate_resource(source, *, checksum=None, extra_checks=None, pick_errors=None, skip_errors=None, limit_errors=config.DEFAULT_LIMIT_ERRORS, limit_memory=config.DEFAULT_LIMIT_MEMORY, noinfer=False, **options, ,)
```

Validate table

API      | Usage
-------- | --------
Public   | `from frictionless import validate_table`

Arguments:

- `source` _any_ - the source of the resource
- `checksum?` _dict_ - a checksum dictionary
- `extra_checks?` _list_ - a list of extra checks
  pick_errors? ((str|int)[]): pick errors
  skip_errors? ((str|int)[]): skip errors
- `limit_errors?` _int_ - limit errors
- `limit_memory?` _int_ - limit memory
- `noinfer?` _bool_ - validate resource as it is
- `**options?` _dict_ - Resource constructor options
  

Returns:

- `Report` - validation report

