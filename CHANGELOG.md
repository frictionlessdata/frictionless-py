# Changelog

Here described only the breaking and most significant changes. The full changelog and documentation for all released versions could be found in nicely formatted [commit history](https://github.com/frictionlessdata/frictionless-py/commits/main).

## v5.15

- Local development has been migrated to using [Hatch](https://hatch.pypa.io/latest/)

## v5.14

- Rebased packaging on PEP 621
- Extracted experimental application/server from the codebase

## v5.13

- Implemented "Metadata.from_descriptor(allow_invalid=False)" (#1501)

## v5.10

- Various architectural and standards-compatibility improvements (minor breaking changes):
    - Added new Console commands:
        - list
        - explore
        - query
        - script
        - convert
        - publish
    - Rebased Console commands on Rich (nice output in the Console)
    - Fixed `extract` returning the results depends on the source type (now it's always a dictionary indexed by the resource name)
    - Enforced type safety -- many tabular command will be marked as impossible for non-tabular resources if a type checker is used
    - Improved `frictionless.Resource(source)` guessing abilities; if you just like to open a table resource use `frictionless.resources.TableResource(path=path)`

## v5.8

- Implemented Implemented `catalog/dataset/package/resource.deference` (#1451)

## v5.7

- Various architectural and standards-compatibility improvements (minor breaking changes):
    - Improved type detection mechanism (including remote descriptors)
    - Added `resources` module including `File/Text/Json/TableResource`
    - Deprecated `resource.type` argument -- use the classes above
    - Changed `catalog.packages[]` to `catalog.datasets[].package`
    - Made `resource.schema` optional (`resource.has_schema` is removed)
    - Made `resource.normpath` optional (`resource.normdata` is removed)
    - Standards-compatability improvements: profile, stats
    - Renamed `system/plugin.select_Check/etc` to `system/plugin.select_check_class/etc`

## v5.6

- Added support for `sqlalchemy@2` (#1427)

## v5.5

- Implemented `program/resource.index` preview (#1395)

## v5.4

- Support `dialect.skip_blank_rows` (#1387)

## v5.3

- Support `steps.resource_update` for resource transformations (#1381)

## v5.2

- Added support for `wkt` format in `fields.StringField` (#1363 by @jze)

## v5.1

- Support `descriptor` argument for `actions/program.extract` (#1372)

## v5.0

- Frictionless Framework (v5) is out of Beta and released on PyPi

## v5.0.0b19

- Implemented [CKAN Integration](https://framework.frictionlessdata.io/docs/portals/ckan.html) ([#1185](https://github.com/frictionlessdata/frictionless-py/issues/1332))

## v5.0.0b8

- ForeignKeyError has been extended with additional information: `fieldNames`, `fieldCells`, `referenceName`, and `referenceFieldNames`

## v5.0.0b2

- Implemented [Github Integration](https://framework.frictionlessdata.io/docs/portals/github.html) ([#1185](https://github.com/frictionlessdata/frictionless-py/issues/1185))

## v5.0.0b1

- First beta version of [Frictionless Framework (v5)](https://framework.frictionlessdata.io/blog/2022/08-22-frictionless-framework-v5.html)

## v4.40

- Added Dialect support to packages (#1137)

## v4.39

- Fixed processing of incompatible decimal char in table schema and data   (#1089)
- Added support for Time Zone data (#1097)
- Improved validation messages by adding `summary` and partial validation details   (#1106)
- Implemented new feature `summary`   (#1127)
    - `schema.to_summary`
    - `report.to_summary`
    - Added CLI command `summary`
- Fixed file compression `package.to_zip`   (#1104)
- Implemented feature to validate single resource   (#1112)
- Improved error message to notify about invalid fields   (#1117)
- Fixed type conversion of NaN values for data of type Int64   (#1115)
- Exposed valid/invalid flags in CLI `extract` command   (#1130)
- Implemented feature `package.to_er_diagram`   (#1135)

## v4.38

- Implemented `checks.ascii_value` (#1064)
- Implemented `checks.deviated_cell` (#1069)
- Implemented `detector.field_true/false_values` (#1074)

## v4.37

- Deprecated high-level legacy actions (use class-based alternatives):
  - `describe_*`
  - `extract_*`
  - `transform_*`
  - `validate_*`

## v4.36

- Implemented pipeline actions:
  - `pipeline.validate` (will replace `validate_pipeline` in v5)
  - `pipeline.transform` (will replace `transform_pipeline` in v5)
- Implemented inqiury actions:
  - `inqiury.validate` (will replace `validate_inqiury` in v5)

## v4.35

- Implemented schema actions:
  - `Schema.describe` (will replace `describe_schema` in v5)
  - `schema.validate` (will replace `validate_schema` in v5)
- Implemented new transform steps:
  - `steps.field_merge`
  - `steps.field_pack`

## v4.34

- Implemented package actions:
  - `Package.describe` (will replace `describe_package` in v5)
  - `package.extract` (will replace `extract_package` in v5)
  - `package.validate` (will replace `validate_package` in v5)
  - `package.transform` (will replace `transform_package` in v5)

## v4.33

- Implemented resource actions:
  - `Resource.describe` (will replace `describe_resource` in v5)
  - `resource.extract` (will replace `extract_resource` in v5)
  - `resource.validate` (will replace `validate_resource` in v5)
  - `resource.transform` (will replace `transform_resource` in v5)

## v4.32

- Added to_markdown() feature to metadata  (#1052)

## v4.31

- Added a feature that allows to export table schema as excel  (#1040)
- Added nontabular note to validation results to indicate nontabular file  (#1046)
- Excel stats now shows bytes and hash  (#1045)
- Added pprint feature which displays metadata in a readable and pretty way  (#1039)
- Improved error message if resource.data is not a string  (#1036)

## v4.29

- Made Detector's private properties public and writable (#1025)

## v4.28

- Improved an order of the metadata in YAML representation

## v4.27

- Exposed Dialect options via CLI such as `sheet`, `table`, `keys`, and `keyed` (#886)

## v4.26

- Validate 'schema.fields[].example' (#998)

## v4.25

- Allows descriptors that subclass collections.abc.Mapping (#985)

## v4.24

- Added support for `SqlDialect.basepath` (#982) (https://framework.frictionlessdata.io/docs/tutorials/formats/sql-tutorial)

## v4.23

- Added table dimensions check (#985)

## v4.22

- Added "extract --trusted" flag

## v4.21

- Added "--json/yaml" CLI options for transform

## v4.20

- Improved layout/schema detection algorithms (#945)

## v4.19

- Renamed `inlineDialect.keys` to `inlineDialect.data_keys` due to a conflict with `dict.keys` property

## v4.18

- Normalized metadata properties (increased type safety)

## v4.17

- Add fields, limit, sort and filter options to CkanDialect (#912)

## v4.16

- Implemented `system/plugin.create_candidates` (#893)

## v4.15

- Implemented `system.get/use_http_session` (#892)

## v4.14

- SQL Where Clause (#882)

## v4.13

- Implemented descriptor type detection for `extract/validate` (#881)

## v4.12

- Support external profiles for data package (#864)

## v4.11

- Added `json` argument to `resource.to_snap`

## v4.10

- Support resource/field renaming in transform (#843)

## v4.9

- Support `--path` CLI argument (#829)

## v4.8

- Added support for `Package(innerpath)` argument for unzipping a data package's descriptor

## v4.7

- Support control/dialect as JSON in CLI (#806)

## v4.6

- Implemented `describe_dialect` and `describe(path, type="dialect")`
- Support `--dialect` argument in CLI

## v4.5

- Implemented `Schema.from_jsonschema` (#797)

## v4.4

- Use `field.constraints.maxLength` for SQL's VARCHAR (#795)

## v4.3

- Implemented `resource.to_view()` (#781)

## v4.2

- Make `fields[].arrayItem` errors more granular (#767)

## v4.1

- Added support for `fields[].arrayItem` (#750)

## v4.0

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
