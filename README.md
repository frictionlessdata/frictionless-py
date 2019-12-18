# goodtables-py

[![Travis](https://img.shields.io/travis/frictionlessdata/goodtables-py/master.svg)](https://travis-ci.org/frictionlessdata/goodtables-py)
[![Coveralls](http://img.shields.io/coveralls/frictionlessdata/goodtables-py.svg?branch=master)](https://coveralls.io/r/frictionlessdata/goodtables-py?branch=master)
[![PyPi](https://img.shields.io/pypi/v/goodtables.svg)](https://pypi.python.org/pypi/goodtables)
[![Github](https://img.shields.io/badge/github-master-brightgreen)](https://github.com/frictionlessdata/goodtables-py)
[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)

Goodtables is a framework to validate tabular data. It can check the structure
of your data (e.g. all rows have the same number of columns), and its contents
(e.g. all dates are valid).

## Features

* **Structural checks**: Ensure that there are no empty rows, no blank headers, etc.
* **Content checks**: Ensure that the values have the correct types ("string", "number", "date", etc.), that their format is valid ("string must be an e-mail"), and that they respect the constraints ("age must be a number greater than 18").
* **Support for multiple tabular formats**: CSV, Excel files, LibreOffice, Data Package, etc.
* **Parallelized validations for multi-table datasets**
* **Command line interface**

## Contents

<!--TOC-->

  - [Getting Started](#getting-started)
    - [Installing](#installing)
    - [Running on CLI](#running-on-cli)
    - [Running on Python](#running-on-python)
  - [Documentation](#documentation)
    - [Report](#report)
    - [Checks](#checks)
    - [Presets](#presets)
    - [Data Quality Errors](#data-quality-errors)
    - [Frequently Asked Questions](#frequently-asked-questions)
  - [API Reference](#api-reference)
    - [`cli`](#cli)
    - [`validate`](#validate)
    - [`preset`](#preset)
    - [`check`](#check)
    - [`Error`](#error)
    - [`spec`](#spec)
    - [`GoodtablesException`](#goodtablesexception)
  - [Contributing](#contributing)
  - [Changelog](#changelog)

<!--TOC-->

## Getting Started

### Installing

> If you have a building error on MacOS please try following this solution - https://github.com/google/jsonnet/issues/573#issuecomment-433201074

```
pip install goodtables
pip install goodtables[ods]  # If you need LibreOffice's ODS file support
```

### Running on CLI

```
goodtables data.csv
```

Use `goodtables --help` to see the different options.

### Running on Python

```python
from goodtables import validate

report = validate('invalid.csv')
report['valid'] # false
report['table-count'] # 1
report['error-count'] # 3
report['tables'][0]['valid'] # false
report['tables'][0]['source'] # 'invalid.csv'
report['tables'][0]['errors'][0]['code'] # 'blank-header'
```

You can read a more in depth explanation on using goodtables with Python on
the [developer documentation](#developer-documentation) section. Check also
the [examples](examples) folder for other examples.

## Documentation

Goodtables validates your tabular dataset to find structural and content
errors. Consider you have a file named `invalid.csv`. Let's validate it:

```python
report = validate('invalid.csv')
```

We could also pass a remote URI instead of a local path. It supports CSV, XLS,
XLSX, ODS, JSON, and all other formats supported by the [tabulator][tabulator]
library.

### Report

> The validation report follows the JSON Schema defined on [goodtables/schemas/report.json][validation-jsonschema].

The output of the `validate()` method is a report dictionary. It includes
information if the data was valid, count of errors, list of table reports, which
individual checks failed, etc. A report will be looking like this:

```json
{
    "time": 0.009,
    "error-count": 1,
    "warnings": [
        "Table \"data/invalid.csv\" inspection has reached 1 error(s) limit"
    ],
    "preset": "table",
    "valid": false,
    "tables": [
        {
            "errors": [
                {
                    "row-number": null,
                    "message": "Header in column 3 is blank",
                    "row": null,
                    "column-number": 3,
                    "code": "blank-header"
                }
            ],
            "error-count": 1,
            "headers": [
                "id",
                "name",
                "",
                "name"
            ],
            "scheme": "file",
            "row-count": 2,
            "valid": false,
            "encoding": "utf-8",
            "time": 0.007,
            "schema": null,
            "format": "csv",
            "source": "data/invalid"
        }
    ],
    "table-count": 1
}
```

The errors are divided in one of the following categories:

- `source` - data can't be loaded or parsed
- `structure` - general tabular errors like duplicate headers
- `schema` - error of checks against [Table Schema](http://specs.frictionlessdata.io/table-schema/)
- `custom` - custom checks errors

### Checks

Check is a main validation actor in goodtables. The list of enabled checks can
be changed using `checks` and `skip_checks` arguments. Let's explore the options
on an example:

```python
report = validate('data.csv') # by default structure and schema (if available) checks
report = validate('data.csv', checks=['structure']) # only structure checks
report = validate('data.csv', checks=['schema']) # only schema (if available) checks
report = validate('data.csv', checks=['bad-headers']) # check only 'bad-headers'
report = validate('data.csv', skip_checks=['bad-headers']) # exclude 'bad-headers'
```

By default a dataset will be validated against all available Data Quality Spec
errors. Some checks can be unavailable for validation. For example, if the
schema isn't provided, only the `structure` checks will be done.

### Presets

Goodtables support different formats of tabular datasets. They're called
presets. A tabular dataset is some data that can be split in a list of data
tables, as:

![Dataset](data/dataset.png)

We can change the preset using the `preset` argument for `validate()`. By
default, it'll be inferred from the source, falling back to `table`. To validate
a [data package][datapackage], we can do:

```python
report = validate('datapackage.json') # implicit preset
report = validate('datapackage.json', preset='datapackage') # explicit preset
```

This will validate all tabular resources in the datapackage.

It's also possible to validate a list of files using the "nested" preset. To do
so, the first argument to `validate()` should be a list of dictionaries, where
each key in the dictionary is named after a parameter on `validate()`. For example:

```python
report = validate([{'source': 'data1.csv'}, {'source': 'data2.csv'}]) # implicit preset
report = validate([{'source': 'data1.csv'}, {'source': 'data2.csv'}], preset='nested') # explicit preset
```

Is similar to:

```python
report_data1 = validate('data1.csv')
report_data2 = validate('data2.csv')
```

The difference is that goodtables validates multiple tables in parallel, so
calling using the "nested" preset should run faster.

### Data Quality Errors

Base report errors are standardized and described in
[Data Quality Spec](https://github.com/frictionlessdata/data-quality-spec/blob/master/spec.json).

#### Source errors

The basic checks can't be disabled, as they deal with goodtables being able to read the files.

| check | description |
| --- | --- |
| io-error | Data reading error because of IO error. |
| http-error | Data reading error because of HTTP error. |
| source-error | Data reading error because of not supported or inconsistent contents. |
| scheme-error | Data reading error because of incorrect scheme. |
| format-error | Data reading error because of incorrect format. |
| encoding-error | Data reading error because of an encoding problem. |

#### Structure errors

These checks validate that the structure of the file are valid.

| check | description |
| --- | --- |
| blank-header | There is a blank header name. All cells in the header row must have a value. |
| duplicate-header | There are multiple columns with the same name. All column names must be unique. |
| blank-row | Rows must have at least one non-blank cell. |
| duplicate-row | Rows can't be duplicated. |
| extra-value | A row has more columns than the header. |
| missing-value | A row has less columns than the header. |

#### Schema errors

These checks validate the contents of the file. To use them, you need to pass a [Table Schema][tableschema]. If you don't have a schema, goodtables can infer it if you use the `infer_schema` option.

If your schema only covers part of the data, you can use the `infer_fields` to infer the remaining fields.

Lastly, if the order of the fields in the data is different than in your schema, enable the `order_fields` option.

| check | description |
| --- | --- |
| schema-error | Schema is not valid. |
| non-matching-header | The header's name in the schema is different from what's in the data. |
| extra-header | The data contains a header not defined in the schema. |
| missing-header | The data doesn't contain a header defined in the schema. |
| type-or-format-error | The value can’t be cast based on the schema type and format for this field. |
| required-constraint | This field is a required field, but it contains no value. |
| pattern-constraint | This field value's should conform to the defined pattern. |
| unique-constraint | This field is a unique field but it contains a value that has been used in another row. |
| enumerable-constraint | This field value should be equal to one of the values in the enumeration constraint. |
| minimum-constraint | This field value should be greater or equal than constraint value. |
| maximum-constraint | This field value should be less or equal than constraint value. |
| minimum-length-constraint | A length of this field value should be greater or equal than schema constraint value. |
| maximum-length-constraint | A length of this field value should be less or equal than schema constraint value. |

#### Custom errors

| check | description |
| --- | --- |
| [blacklisted-value](#blacklisted-value) | Ensure there are no cells with the blacklisted values. |
| [deviated-value](#deviated-value) | Ensure numbers are within a number of standard deviations from the average. |
| [foreign-key](#foreign-key) | Ensure foreign keys are valid within a data package |
| [sequential-value](#sequential-value) | Ensure numbers are sequential. |
| [truncated-value](#truncated-value) | Detect values that were potentially truncated. |
| [custom-constraint](#custom-constraint) | Defines a constraint based on the values of other columns (e.g. `value * quantity == total`). |

##### blacklisted-value

Sometimes we have to check for some values we don't want to have in out dataset. It accepts following options:

| option | type | description |
| --- | --- | --- |
| column | int/str | Column number or name |
| blacklist | list of str | List of blacklisted values |

Consider the following CSV file:

```csv
id,name
1,John
2,bug
3,bad
5,Alex
```

Let's check that the `name` column doesn't contain rows with `bug` or `bad`:

```python
from goodtables import validate

report = validate('data.csv', checks=[
    {'blacklisted-value': {'column': 'name', 'blacklist': ['bug', 'bad']}},
])
# error on row 3 with code "blacklisted-value"
# error on row 4 with code "blacklisted-value"
```

##### deviated-value

This check helps to find outlines in a column containing positive numbers. It accepts following options:

| option | type | description |
| --- | --- | --- |
| column | int/str | Column number or name |
| average | str | Average type, either "mean", "median" or "mode" |
| interval | int | Values must be inside range `average ± standard deviation * interval` |

Consider the following CSV file:

```csv
temperature
1
-2
7
0
1
2
5
-4
100
8
3
```

We use `median` to get an average of the column values and allow interval of 3 standard deviations. For our case median is `2.0` and standard deviation is `29.73` so all valid values must be inside the `[-87.19, 91.19]` interval.

```python
report = validate('data.csv', checks=[
    {'deviated-value': {'column': 'temperature', 'average': 'median', 'interval': 3}},
])
# error on row 10 with code "deviated-value"
```

##### foreign-key

> We support here relative paths. It MUST be used only for trusted data sources.

This check validate foreign keys within a data package. Consider we have a data package defined below:

```python
DESCRIPTOR = {
  'resources': [
    {
      'name': 'cities',
      'data': [
        ['id', 'name', 'next_id'],
        [1, 'london', 2],
        [2, 'paris', 3],
        [3, 'rome', 4],
        # [4, 'rio', None],
      ],
      'schema': {
        'fields': [
          {'name': 'id', 'type': 'integer'},
          {'name': 'name', 'type': 'string'},
          {'name': 'next_id', 'type': 'integer'},
        ],
        'foreignKeys': [
          {
            'fields': 'next_id',
            'reference': {'resource': '', 'fields': 'id'},
          },
          {
            'fields': 'id',
            'reference': {'resource': 'people', 'fields': 'label'},
          },
        ],
      },
    }, {
      'name': 'people',
      'data': [
        ['label', 'population'],
        [1, 8],
        [2, 2],
        # [3, 3],
        # [4, 6],
      ],
    },
  ],
}
```

Running `goodtables` on it will raise a few `foreign-key` errors because we have commented some rows in the data package's data:

```python
report = validate(DESCRIPTOR, checks=['structure', 'schema', 'foreign-key'])
print(report)
```

```
{'error-count': 2,
 'preset': 'datapackage',
 'table-count': 2,
 'tables': [{'datapackage': '...',
             'error-count': 2,
             'errors': [{'code': 'foreign-key',
                         'message': 'Foreign key "[\'next_id\']" violation in '
                                    'row 4',
                         'message-data': {'fields': ['next_id']},
                         'row-number': 4},
                        {'code': 'foreign-key',
                         'message': 'Foreign key "[\'id\']" violation in row 4',
                         'message-data': {'fields': ['id']},
                         'row-number': 4}],
             'format': 'inline',
             'headers': ['id', 'name', 'next_id'],
             'resource-name': 'cities',
             'row-count': 4,
             'schema': 'table-schema',
             'source': 'inline',
             'time': 0.031,
             'valid': False},
            {'datapackage': '...',
             'error-count': 0,
             'errors': [],
             'format': 'inline',
             'headers': ['label', 'population'],
             'resource-name': 'people',
             'row-count': 3,
             'source': 'inline',
             'time': 0.038,
             'valid': True}],
 'time': 0.117,
 'valid': False,
 'warnings': []}
```

It experimetally supports external resource checks, for example, for a `foreignKey` definition like these:

```json
{"package": "../people/datapackage.json", "resource": "people", "fields": "label"}
{"package": "http:/example.com/datapackage.json", "resource": "people", "fields": "label"}
```

##### sequential-value

This checks is for pretty common case when a column should have integers that sequentially increment.  It accepts following options:

| option | type | description |
| --- | --- | --- |
| column | int/str | Column number or name |

Consider the following CSV file:

```csv
id,name
1,one
2,two
3,three
5,five
```

Let's check if the `id` column contains sequential integers:

```python
from goodtables import validate

report = validate('data.csv', checks=[
    {'sequential-value': {'column': 'id'}},
])
# error on row 5 with code "sequential-value"
```

##### truncated-value

Some database or spreadsheet software (like MySQL or Excel) could cutoff values on saving. There are some well-known heuristics to find this bad values. See https://github.com/propublica/guides/blob/master/data-bulletproofing.md for more detailed information.

Consider the following CSV file:

```csv
id,amount,comment
1,14000000,good
2,2147483647,bad
3,32767,bad
4,234234234,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbad
```

To detect all probably truncated values we could use `truncated-value` check:

```python
report = validate('data.csv', checks=[
    'truncated-value',
])
# error on row 3 with code "truncated-value"
# error on row 4 with code "truncated-value"
# error on row 5 with code "truncated-value"
```

##### custom-constraint

With Table Schema we could create constraints for an individual field but sometimes it's not enough. With a custom constraint check every row could be checked against given limited python expression in which variable names resolve to column values. See list of [available operators]( https://github.com/danthedeckie/simpleeval#operators). It accepts following options:

<dl>
  <dt>constraint (str)</dt>
  <dd>Constraint definition (e.g. <code>col1 + col2 == col3</code>)</dd>
</dl>

Consider csv file like this:

```csv
id,name,salary,bonus
1,Alex,1000,200
2,Sam,2500,500
3,Ray,1350,500
4,John,5000,1000
```

Let's say our business rule is to be shy on bonuses:

```python
report = validate('data.csv', checks=[
    {'custom-constraint': {'constraint': 'salary > bonus * 4'}},
])
# error on row 4 with code "custom-constraint"
```

### Frequently Asked Questions

#### How can I add a new custom check?

To create a custom check user could use a `check` decorator. This way the builtin check could be overridden (use the spec error code like `duplicate-row`) or could be added a check for a custom error (use `type`, `context` and `position` arguments):

```python
from goodtables import validate, check, Error

@check('custom-check', type='custom', context='body')
def custom_check(cells):
    errors = []
    for cell in cells:
        message = 'Custom error on column {column_number} and row {row_number}'
        error = Error(
            'custom-error',
            cell,
            message
        )
        errors.append(error)
    return errors

report = validate('data.csv', checks=['custom-check'])
```

For now this documentation section is incomplete. Please see builtin checks to learn more about checking protocol.

#### How can I add support for a new tabular file type?

To create a custom preset user could use a `preset` decorator. This way the builtin preset could be overridden or could be added a custom preset.

```python
from tabulator import Stream
from tableschema import Schema
from goodtables import validate

@preset('custom-preset')
def custom_preset(source, **options):
    warnings = []
    tables = []
    for table in source:
        try:
            tables.append({
                'source':  str(source),
                'stream':  Stream(...),
                'schema': Schema(...),
                'extra': {...},
            })
        except Exception:
            warnings.append('Warning message')
    return warnings, tables

report = validate(source, preset='custom-preset')
```

For now this documentation section is incomplete. Please see builtin presets to learn more about the dataset extraction protocol.

## API Reference

### `cli`
```python
cli()
```
Command-line interface

```
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  validate*  Validate tabular files (default).
  init       Init data package from list of files.
```


### `validate`
```python
validate(source, **options)
```
Validates a source file and returns a report.

__Arguments__

- __source (Union[str, Dict, List[Dict], IO])__:
        The source to be validated.
        It can be a local file path, URL, dict, list of dicts, or a
        file-like object. If it's a list of dicts and the `preset` is
        "nested", each of the dict key's will be used as if it was passed
        as a keyword argument to this method.

        The file can be a CSV, XLS, JSON, and any other format supported by
        `tabulator`_.
- __checks (List[str])__:
        List of checks names to be enabled. They can be
        individual check names (e.g. `blank-headers`), or check types (e.g.
        `structure`).
- __skip_checks (List[str])__:
        List of checks names to be skipped. They can
        be individual check names (e.g. `blank-headers`), or check types
        (e.g.  `structure`).
- __infer_schema (bool)__:
        Infer schema if one wasn't passed as an argument.
- __infer_fields (bool)__:
        Infer schema for columns not present in the received schema.
- __order_fields (bool)__:
        Order source columns based on schema fields order.
        This is useful when you don't want to validate that the data
        columns' order is the same as the schema's.
- __error_limit (int)__:
        Stop validation if the number of errors per table exceeds this value.
- __table_limit (int)__:
        Maximum number of tables to validate.
- __row_limit (int)__:
        Maximum number of rows to validate.
- __preset (str)__:
        Dataset type could be `table` (default), `datapackage`,
        `nested` or custom. Usually, the preset can be inferred from the
        source, so you don't need to define it.
- __Any (Any)__:
        Any additional arguments not defined here will be passed on,
        depending on the chosen `preset`. If the `preset` is `table`, the
        extra arguments will be passed on to `tabulator`_, if it is
        `datapackage`, they will be passed on to the `datapackage`_
        constructor.

__Raises__
- `GoodtablesException`: Raised on any non-tabular error.

__Returns__

`dict`: The validation report.


### `preset`
```python
preset(name)
```
Register a custom preset (decorator)

__Example__


```python
@preset('custom-preset')
def custom_preset(source, **options):
    # ...
```

__Arguments__
- __name (str)__: preset name


### `check`
```python
check(name, type=None, context=None, position=None)
```
Register a custom check (decorator)

__Example__


```python
@check('custom-check', type='custom', context='body')
def custom_check(cells):
    # ...
```

__Arguments__
- __name (str)__: preset name
- __type (str)__: has to be `custom`
- __context (str)__: has to be `head` or `body`
- __position (str)__: has to be `before:<check-name>` or `after:<check-name>`


### `Error`
```python
Error(self, code, cell=None, row_number=None, message=None, message_substitutions=None)
```
Describes a validation check error

__Arguments__
- __code (str)__: The error code. Must be one in the spec.
- __cell (dict, optional)__: The cell where the error occurred.
- __row_number (int, optional)__: The row number where the error occurs.
- __message (str, optional)__:
        The error message. Defaults to the message from the Data Quality Spec.
- __message_substitutions (dict, optional)__:
        Dictionary with substitutions to be used when
        generating the error message and description.

__Raises__
- `KeyError`: Raised if the error code isn't known.


### `spec`
dict() -> new empty dictionary
dict(mapping) -> new dictionary initialized from a mapping object's
    (key, value) pairs
dict(iterable) -> new dictionary initialized as if via:
    d = {}
    for k, v in iterable:
        d[k] = v
dict(**kwargs) -> new dictionary initialized with the name=value pairs
    in the keyword argument list.  For example:  dict(one=1, two=2)
### `GoodtablesException`
```python
GoodtablesException(self, /, *args, **kwargs)
```
Base goodtables exception

## Contributing

> The project follows the [Open Knowledge International coding standards](https://github.com/okfn/coding-standards).

Recommended way to get started is to create and activate a project virtual environment.
To install package and development dependencies into active environment:

```bash
$ make install
```

To run tests with linting and coverage:

```bash
$ make test
```

## Changelog

Here described only breaking and the most important changes. The full changelog and documentation for all released versions could be found in nicely formatted [commit history](https://github.com/frictionlessdata/goodtables-py/commits/master).

##### v2.4

- Added integrity checks for data packages. If `resource.bytes` or `resource.hash` (sha256) is provided it will be verified against actual values

##### v2.3

- Added a [foreign keys check](#foreign-key)

##### v2.2

- Improved missing/non-matching-headers detection ([#298](https://github.com/frictionlessdata/goodtables-py/issues/298))

##### v2.1

- A new key added to the `error.to_dict` return: `message-data`

##### v2.0

Breaking changes:

- Checks method signature now only receives the current row's `cells` list
- Checks raise errors by returning an array of `Error` objects
- Cells have the row number in the `row-number` key
- Files with ZIP extension are presumed to be datapackages, so `goodtables mydatapackage.zip` works
- Improvements to goodtables CLI ([#233](https://github.com/frictionlessdata/goodtables-py/issues/233))
- New `goodtables init <data paths>` command to create a new `datapackage.json` with the files passed as parameters and their inferred schemas.

Bug fixes:
- Fix bug with `truncated-values` check on date fields ([#250](https://github.com/frictionlessdata/goodtables-py/issues/250))

##### v1.5

New API added:
- Validation `source` now could be a `pathlib.Path`

##### v1.4

Improved behaviour:
- rebased on Data Quality Spec v1
- rebased on Data Package Spec v1
- rebased on Table Schema Spec v1
- treat primary key as required/unique field

##### v1.3

New advanced checks added:
- `blacklisted-value`
- `custom-constraint`
- `deviated-value`
- `sequential-value`
- `truncated-value`

##### v1.2

New API added:
- `report.preset`
- `report.tables[].schema`

##### v1.1

New API added:
- `report.tables[].scheme`
- `report.tables[].format`
- `report.tables[].encoding`

##### v1.0

This version includes various big changes. A migration guide is under development and will be published here.

##### v0.6

First version of `goodtables`.

[tableschema]: https://specs.frictionlessdata.io/table-schema/
[tabulator]: https://github.com/frictionlessdata/tabulator-py/
[datapackage]: https://specs.frictionlessdata.io/data-package/ "Data Package specification"
[semver]: https://semver.org/ "Semantic Versioning"
[validation-jsonschema]: goodtables/schemas/report.json "Validation Report JSON Schema"
