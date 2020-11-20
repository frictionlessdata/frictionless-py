# Changelog

Here described only the breaking and most significant changes. The full changelog and documentation for all released versions could be found in nicely formatted [commit history](https://github.com/frictionlessdata/frictionless-py/commits/master).

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
