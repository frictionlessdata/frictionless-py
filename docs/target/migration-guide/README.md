# Migration Guide

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1eWGtfAgD4mkvyT2BcqU3Y68Yg25ZrlU-)



Frictionless is a logical continuation of many currently existent package:
- goodtables
- datapackage
- tableschema
- tableschema-drivers
- tabulator

Although, most of these packages will be supported going forward, you can migrate to Frictionless as it improves many aspects of working with data and metadata.

## From goodtables

Frictionless provides the `frictionless validate` function which is in high-level exactly the same as `goodtables validate`. Also `frictionless describe` is an improved version of `goodtables init`. You just need to use the `frictionless` command instead of the `goodtables` command:

```bash
# Before
$ goodtables validate table.csv
# After
$ frictionless validate  table.csv
```

The Python interface is also mostly identical:

```python
# Before
report = goodtables.validate('table.csv')
# After
report = frictonles.validate('table.csv')
```


Please read the following sections and use `frictionless validate --help` to learn what is the difference in the options and in report's properties.

### Validate

- a schema is inferred by default (use "Infer Options" and "Schema Options" to manage)
- `order_fiels` was replaced by `sync_schema` (see "Schema Options")
- `checks` was replaced by `pick/skip_errors` and `extra_checks`
- `error_limit` was replaced by `limit_errors` (see "Errors Options")
- `row_limit` was replaced by `query` (see "Table Query)
- `preset` was replaced by `source_type`


### Report

- all the properties now are camelCased instead of being lower-cased
- various error code changes (see "Errors Reference")
- errors now have both row position and row number
- `row-number` was replaced by `rowPosition`
- high-level `warnings` was replaced by `errors`

## From datapackage

Frictionless has `Resource` and `Package` classes which is almost the same as `datapackage` has. There are a lot of improvements for working with metadata described in the "Describing Data" guide.

```python
# Before
resource = datapackage.Resource('resource.json')
package = datapackage.Package('package.json')
# After
resource = frictionless.Resource('resource.json')
package = frictionless.Package('package.json')
```

### Package

- added YAML support
- the Package object is now a dict
- there is no `package.descriptor` anymore
- it's now possible to use keyword arguments in the constructor
- it's now possible to use attribute setters to update a package
- `package.save` is replaced by `package.to_json`

### Resource

- added YAML support
- the Resource object is now a dict
- there is no `resource.descriptor` anymore
- it's now possible to use keyword arguments in the constructor
- it's now possible to use attribute setters to update a resource
- `resource.save` is replaced by `**resource**.to_json`
- `resource.read` was replaced by `resource.read_data/rows`
- `resource.iter` was replaced by `resource.stream_data/rows`
- `resource.raw_read` was replaced by `resource.read_bytes`
- `resource.raw_iter` was replaced by `resource.stream_bytes`

## From tableschema

Frictionless has `Schema` and `Fiels` classes which is almost the same as `tableschema` has. There are a lot of improvements for working with metadata described in the "Describing Data" guide.

```python
# Before
schema = tableschema.Schema('schema.json')
field = tableschema.Field('field.json')
# After
schema = frictionless.Schema('schema.json')
field = frictionless.Field('field.json')
```

### Schema

- added YAML support
- the Package object is now a dict
- there is no `schema.descriptor` anymore
- it's now possible to use keyword arguments in the constructor
- it's now possible to use attribute setters to update a schema
- `schema.save` is replaced by `schema.to_json`
- `schema.cast_row` is replaced by `schema.read_data`

### Field

- added YAML support
- the Resource object is now a dict
- there is no `resource.descriptor` anymore
- it's now possible to use keyword arguments in the constructor
- it's now possible to use attribute setters to update a resource
- `field.save` is replaced by `field.to_json`
- `field.cast_value` is replaced by `field.read_cell`

## From tabulator


Frictionless has `Table` class which is an equivalent of the tabulator's `Stream` class.

```python
# Before
with tabulator.Stream('table.csv') as stream:
  print(stream.read())
# After
with frictionless.Table('table.csv') as table:
  print(table.read_rows())
```


### Table

- the Table class now always infers `table.schema`
- `table.read` was replace by `table.read_data/rows`
- `table.iter` was replaced by `table.data/row_stream`
- `table.hash/size` was replaced by the `table.stats` property
- various changes in the constructor options (see "Extracting Data")