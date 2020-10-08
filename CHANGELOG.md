# Changelog

Here described only the breaking and most significant changes. The full changelog and documentation for all released versions could be found in nicely formatted [commit history](https://github.com/frictionlessdata/frictionless-py/commits/master).

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
