# Changelog

Here described only the breaking and most significant changes. The full changelog and documentation for all released versions could be found in nicely formatted [commit history](https://github.com/frictionlessdata/frictionless-py/commits/main).

## v4.19.0

- Renamed `inlineDialect.keys` to `inlineDialect.data_keys` due to a conflict with `dict.keys` property

## v4.18.0

- Normalized metadata properties (increased type safety)

## v4.17.0

- Add fields, limit, sort and filter options to CkanDialect (#912)

## v4.16.0

- Implemented `system/plugin.create_candidates` (#893)

## v4.15.0

- Implemented `system.get/use_http_session` (#892)

## v4.14.0

- SQL Where Clause (#882)

## v4.13.0

- Implemented descriptor type detection for `extract/validate` (#881)

## v4.12.0

- Support external profiles for data package (#864)

## v4.11.0

- Added `json` argument to `resource.to_snap`

## v4.10.0

- Support resource/field renaming in transform (#843)

## v4.9.0

- Support `--path` CLI argument (#829)

## v4.8.0

- Added support for `Package(innerpath)` argument for unzipping a data package's descriptor

## v4.7.0

- Support control/dialect as JSON in CLI (#806)

## v4.6.0

- Implemented `describe_dialect` and `describe(path, type="dialect")`
- Support `--dialect` argument in CLI

## v4.5.0

- Implemented `Schema.from_jsonschema` (#797)

## v4.4.0

- Use `field.constraints.maxLength` for SQL's VARCHAR (#795)

## v4.3.0

- Implemented `resource.to_view()` (#781)

## v4.2.0

- Make `fields[].arrayItem` errors more granular (#767)

## v4.1.0

- Added support for `fields[].arrayItem` (#750)

## v4.0.0

- Released `frictionless@4` :tada:

## v4.0.0a15

- Updated loaders (#658) (BREAKING)
    - Renamed `filelike` loader to `stream` loader
    - Migrated from `text` loader to `buffer` loader

## v4.0.0a14

- Improve transform API (#657) (BREAKING)
    - Swithed to the `transform_resource(resource)` signature
    - Swithed to the `transform_package(package)` signature

## v4.0.0a13

- Improved resource/package import/export (#655) (BREAKING)
    - Reworked `parser.write_row_stream` API
    - Reworked `resource.from/to` API
    - Reworked `package.from/to` API
    - Reworked `Storage` API
    - Reworked `system.create_storage` API
    - Merged `PandasStorage` into `PandasParser`
    - Merged `SpssStorage` into `SpssParser`

## v4.0.0a12

- Improved transformation steps (#650) (BREAKING)
    - Split value/formula/function concepts
    - Renamed a few minor step arguments

## v4.0.0a11

- Improved layout and data streams concepts (#648) (BREAKING)
    - Renamed `data_stream` to `list_stream`
    - Renamed `readData` to `readLists`
    - Renamed `sample` to `fragment` (`sample` now is raw lists)
    - Implemented loader.buffer
    - Implemented parser.sample
    - Added support for function based checks
    - Added support for function based steps

## v4.0.0a10

- Reworked Error.tags (BREAKING)
- Reworked Check API and split labels/header (BREAKING)

## v4.0.0a9

- Rebased on `Detector` class (BREAKING)
    - Migrated all infer_*, sync/patch_schema and detect_encoding parameters to `Detector`
    - Made `resource.infer` omit empty objects
    - Added `resource.read_*(size)` argument
    - Added `resource.labels` property

## v4.0.0a8

- Improved checks/steps API (#621) (BREAKING)
    - Updated `validate(extra_checks=[...])` to `validate(checks=[{"code": 'code', ...}])`

## v4.0.0a7

- Updated describe/extract/transform/validate APIs (BREAKING)
    - Removed `validate_table` (use `validate_resource`)
    - Removed legacy `Table` and `File` classes
    - Removed `dataflows` plugin
    - Replaced `nopool` by `parallel` (not parallel by default)
    - Renamed `report.tables` to `report.tasks`
    - Rebased on `report.tasks[].resource` (instead of plain path/scheme/format/etc)
    - Flatten Pipeline steps signature

## v4.0.0a6

- Introduced Layout class (BREAKING)
    - Renamed `Query` class and arguments/properties to `Layout`
    - Moved `header` options from `Dialect` to `Layout`

## v4.0.0a5

- Updated transform API
    - Added `transform(type)` argument

## v4.0.0a4

- Updated describe API (BREAKING)
    - Renamed `describe(source_type)` argument to `type`

## v4.0.0a3

- Updated extract API (BREAKING)
    - Removed `extract_table` (use `extract_resource` with the same API)
    - Renamed `extract(source_type)` argument to `type`

## v4.0.0a1

- Initial API/codebase improvements for v4 (BREAKING)
    - Allow `Package/Resource(source)` notation (guess descriptor/path/etc)
    - Renamed `schema.infer` -> `Schema.from_sample`
    - Renamed `resource.inline` -> `resource.memory`
    - Renamed `compression_path` -> `innerpath`
    - Renamed `compression: no` -> `compression: ""`
    - Updated `Package/Resource.infer` not to infer stats (use `stats=True`)
    - Removed `Package/Resource.infer(only_sample)` argument
    - Removed `Resouce.from/to_zip` (use `Package.from/to_zip`)
    - Removed `Resouce.source` (use `Resource.data` or `Resource.fullpath`)
    - Removed `package/resource.infer(source)` argument (use constructors)
    - Added some new API (will be covered in the updated docs after the v4 release)

## v3.48

- Make Resource independent from Table/File (#607) (BREAKING)
    - Resource can be opened like Table (it's recommended to use Resource instead of Table)
    - Renamed `resource.read_sample()` to `resource.sample`
    - Renamed `resource.read_header()` to `resource.header`
    - Renamed `resource.read_stats()` to `resource.stats`
    - Removed `resource.to_table()`
    - Removed `resource.to_file()`

## v3.47

- Optimize Row/Header/Table and rename header errors (#601) (BREAKING)
    - Row object is now lazy; it casts data on-demand preserving the same API
    - Method `resource/table.read_data(_stream)` now includes a header row if present
    - Renamed `errors.ExtraHeaderError->ExtraLabelError` (`extra-label-error`)
    - Renamed `errors.MissingHeaderError->MissingLabelError` (`missing-label-error`)
    - Renamed `errors.BlankHeaderError->BlankLabelError` (`blank-label-error`)
    - Renamed `errors.DuplicateHeaderError->DuplicateLabelError` (`duplicate-label-error`)
    - Renamed `errors.NonMatchingHeaderError->IncorrectLabelError` (`incorrect-label-error`)
    - Renamed `schema.read/write_data->read/write_cells`

## v3.46

- Renamed aws plugin to s3 (#594) (BREAKING)

```bash
$ pip install frictionless[aws] # before
$ pip install frictionless[s3] # after
```

## v3.45

- Drafted support for writing Multipart Data (#583)

## v3.44

- Added support for writing to Remote Data (#582)

## v3.43

- Add support to writing to Google Sheets (#581)
- Renamed `gsheet` plugin/format to `gsheets` (BREAKING: minor)

## v3.42

- Added support for writing to S3 (#580)

## v3.41

- Update Loader/Parser API to write to different targets (#579) (BREAKING: minor)

## v3.40

- Implemented a standalone multipart loader (#573)

## v3.39

- Fixed Header not being an original one (#572)
- Fix bad format validation (#571)
- Added default errors limit equals to 1000 (#570)
- Added support for field.float_number (#569)

## v3.38

- Improved ckan plugin (#560)

## v3.37

- Remove not working elastic plugin draft (#558)

## v3.36

- Support custom types (#557)

## v3.35

- Added "resolve" option to "resource/package.to_zip" (#556)

## v3.34

- Moved `frictionless.controls` to `frictionless.plugins.*` (BREAKING)
- Moved `frictionless.dialects` to `frictionless.plugins.*` (BREAKING)
- Moved `frictionless.exceptions.FrictionlessException` to `frictionless.FrictionlessException` (BREAKING)
- Moved `excel` dependencies to `frictionless[excel]` extras (BREAKING)
- Moved `json` dependencies to `frictionless[json]` extras (BREAKING)
- Consider `json` files to be a metadata by default (BREAKING)

Code example:

```python
# Before
# pip install frictionless
from frictionless import dialects, exceptions
excel_dialect = dialects.ExcelDialect()
json_dialect = dialects.JsonDialect()
exception = exceptions.FrictionlessException()

# After
# pip install frictionless[excel,json]
from frictionless import FrictionlessException
from frictionless.plugins.excel import ExcelDialect
from frictionless.plugins.json import JsonDialect
excel_dialect = dialects.ExcelDialect()
json_dialect = dialects.JsonDialect()
exception = FrictionlessException()
```

## v3.33

- Implemented resource.write (#537)

## v3.32

- Added url parameter to SQL import/export (#535)

## v3.31

- Made tables with header and no data rows valid (#534) (BREAKING: minor)

## v3.30

- Various CLI improvements (#532)
    - Added autocompletion
    - Added stdin support
    - Added "extract --csv"
    - Exposed more options

## v3.29

- Added experimental CKAN support (#528)

## v3.28

- Add a "nopool" argument to validate (#527)

## v3.27

- Stop sorting keyed sources as the order is now guaranteed by Python (#512) (BREAKING)

## v3.26

- Added "nolookup" argument for validate_package (#515)

## v3.25

- Add transform functionality (#505)
- Methods `schema.get/remove_field` now raise if not found (#505) (BREAKING)
- Methods `package.get/remove_resource` now raise if not found (#505) (BREAKING)

## v3.24

- Lower case resource.scheme/format/hashing/encoding/compression (#499) (BREAKING)

## v3.23

- Support "header_case" option for dialects (#488)

## v3.22

- Added suppport for DB2 format (#485)

## v3.21

- Improved SPSS plugin (#483)
- Improved BigQuery plugin (#470)

## v3.20

- Added support for SQL Views (#466)

## v3.19

- Rebased AwsLoader on streaming (#460)

## v3.18

- Added `hashing` parameter to `describe/describe_package`
- Removed `table.onerror` property (BREAKING)

## v3.17

- Added timezone for datetime/time parsing (#457) (BREAKING)

## v3.16

- Fixed metadata.to_yaml (#455)
- Removed the `expand` argument from `metadata.to_dict` (BREAKING)

## v3.15

- Added native schema support to SqlParser (#452)

## v3.14

- Make Resource the main internal interface (#446) (BREAKING: for plugin authors)
- Move Resource's stats to `resource.stats` (BREAKING)
- Rename `on_error` to `onerror` (BREAKING)
- Added `resource.stats.fields`

## v3.13

- Add an `on_error` argument to Table/Resource/Package (#445)

## v3.12

- Added streaming to the extract functions (#442)

## v3.11

- Added experimental BigQuery support (#424)

## v3.10

- Added experimental SPSS support (#421)

## v3.9

- Rebased on a `goodtables` successor versioning

## v3.8

- Add support SQL/Pandas import/export  (#31)

## v3.7

- Add support for custom JSONEncoder classes (#24)

## v3.6

- Normalize header terminology

## v3.5

- Initial public version
