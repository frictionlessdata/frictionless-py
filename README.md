# goodtables

[![Travis](https://img.shields.io/travis/frictionlessdata/goodtables/master.svg)](https://travis-ci.org/frictionlessdata/goodtables)
[![Coveralls](http://img.shields.io/coveralls/frictionlessdata/goodtables.svg?branch=master)](https://coveralls.io/r/frictionlessdata/goodtables?branch=master)
[![PyPi](https://img.shields.io/pypi/v/goodtables.svg)](https://pypi.python.org/pypi/goodtables)
[![SemVer](https://img.shields.io/badge/versions-SemVer-brightgreen.svg)](http://semver.org/)
[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)

Goodtables is a simple utility library to inspect tabular data.

## Features

- tabular data inspection and validation
- source, structure and schema checks
- support of different input data profiles
- parallel computation for multitable profiles
- builtin command-line interface

## Getting Started

### Installation

```
$ pip install goodtables
```

### Example

Let's start with the simple example:

```python
from goodtables import Inspector

inspector = Inspector()
print(inspector.inspect('data/invalid.csv'))

# will print
#{'time': 0.029,
# 'valid': False',
# 'error-count': 2,
# 'table-count': 1,
# 'errors': [],
# 'tables': [
#    {'time': 0.027,
#     'valid': False',
#     'headers': ['id', 'name', ''],
#     'row-count': 4,
#     'error-count': 2,
#     'errors': [
#        {'row': None,
#         'code': 'blank-header',
#         'message': 'Blank header',
#         'row-number': None,
#         'col-number': 2},
#        {'row': [],
#         'code': 'blank-row',
#         'message': 'Blank row',
#         'row-number': 3,
#         'col-number': None}]}]}
```

### Overview

Goodtables inspects your tabular data to find errors in source, structure and schema. As presented in an example above to inspect data:
- `Inspector(**options)` class should be instantiated
- `inspector.inspect(source, profile='table', **options)` should be called
- a returning value will be a report dictionary

All errors in a report are standartised and described in data quality spec - https://github.com/roll/goodtables-next/tree/master/goodtables/spec.json. Errors are mentioned in order of actual check.

#### Error types

- source errors - data can't be loaded or parsed
- structure errors - general tabular errors like duplicate headers
- schema errors - error of checks against JSON Table Schema

#### Error contexts

- table - the whole table errors like bad encoding
- head - headers errors
- body - contents errors

Contexts and field/rows coordinates are presented on a figure 1:

![Table](files/table.png)

### Profiles

Table is a main concept in goodtables. The simplest option is to pass to `Inspector.inspect` path and other options for one table (see example above). But when multitable parallized inspection is needed profiles could be used to process a dataset.

Goodtables supports the following profiles:
- table
- datapackage
- ckan

A profile proceses passed source and options and return it as a dataset containing tables with extras for the following inspection.

### Checks

List of checks for an inspection could be customized on `Inspector.inspect` call. Let's explore options on an example:

```python
inspector = Inspector()
inspector.inspect('path.csv', checks='structure/schema') # presets
inspector.inspect('path.csv', checks={'bad-headers': False}) # exclude
inspector.inspect('path.csv', checks={'bad-headers': True}) # include
```

## Documentation

### Inspector

An API definition:

```
Inspector(checks='all',
          table_limit=10,
          row_limit=1000,
          error_limit=1000)
    inspect(source, profile='table', **options)
```

### exceptions

The library provides various of exceptions. Please consult with docstrings.

### CLI

> CLI is not a part of SemVer versionning. If you use it programatically please pin concrete `goodtables` version to your requirements file.

All common goodtables tasks could be done using a command-line interface (command per profile):

```
$ python -m goodtables.cli
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --table-limit INTEGER
  --row-limit INTEGER
  --error-limit INTEGER
  --help                 Show this message and exit.

Commands:
  ckan
  datapackage
  table
```

For example write a following command to the shell:

```
$ python -m goodtables.cli table data/invalid.csv
```

And a report (the same as in the initial example) will be printed to the standard output.

## FAQ

### Is it an inspection or validation?

For now we use `inspector` word because we create reports as result of an inspection. One difference to validation - goodtables will not raise an exception if dataset is invalid.  Final naming is under considiration and based on exposed methods (only `inspect` or like `inspect/validate/stream`).

### Is it possible to stream reporting?

For now - it's not. But it's under considiration. Not for multitable profiles because of parallelizm but for one table it could be exposed to public API because internally it's how goodtables works. Question here is what should be streamed - errors or valid/invalid per row indication with errors etc. We would be happy to see a real world use case for this feature.

### Is it possible to use custom profile?

For now public API for custom profiles is not available. If it will be implemented an interface will be simple:

```python
from goodtables import Inspector
from jsontableschema import Table

def custom_profile(source, **options):
    dataset = []
    for item in source:
        dataset.append({
            'table': Table(...),
            'extra': {...},
        })
    return dataset

inspector = Inspector()
inspector.inspect(source, profile=custrom_profile)
```

### Is it possible to use custom checks?

For now public API for custom checks is not available. If it will be implemented an interface will be simple (an example for the `body` context):

```python
from goodtables import Inspector

def custom_check(cells, sample):
    errors = []
    for cell in cells:
        errors.append({
            'message': 'Custom error',
            'row-number': cell['row-number'],
            'col-number': cell['row-number'],
        })
    return errors

inspector = Inspector(custom_checks=[{
    'after': 'duplicate-headers',
    'func': custom_check,
    'code': 'custom-check',
    'type': 'structure',
    'context': 'body',
    'requires': [],
}])
```

## Read More

- [Docstrings](https://github.com/frictionlessdata/goodtables-py/tree/master/goodtables)
- [Changelog](https://github.com/frictionlessdata/goodtables/commits/master)
- [Contribute](CONTRIBUTING.md)

Thanks!
