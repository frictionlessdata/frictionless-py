# goodtables

[![Travis](https://img.shields.io/travis/frictionlessdata/goodtables/master.svg)](https://travis-ci.org/frictionlessdata/goodtables)
[![Coveralls](http://img.shields.io/coveralls/frictionlessdata/goodtables.svg?branch=master)](https://coveralls.io/r/frictionlessdata/goodtables?branch=master)
[![PyPi](https://img.shields.io/pypi/v/goodtables.svg)](https://pypi.python.org/pypi/goodtables)
[![SemVer](https://img.shields.io/badge/versions-SemVer-brightgreen.svg)](http://semver.org/)
[![Gitter](https://img.shields.io/gitter/room/frictionlessdata/chat.svg)](https://gitter.im/frictionlessdata/chat)

Goodtables is a framework to inspect tabular data.

> Version v0.8 has renewed API introduced in NOT backward-compatibility manner. Previous version could be found [here](https://github.com/frictionlessdata/goodtables-py/tree/4b85254cc0358c0caf85bbd41d0c2023df99fb9b).

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
#         'column-number': 2},
#        {'row': [],
#         'code': 'blank-row',
#         'message': 'Blank row',
#         'row-number': 3,
#         'column-number': None}]}]}
```

### Inspection

Goodtables inspects your tabular data to find errors in source, structure and schema. As presented in an example above to inspect data:
- `Inspector(**options)` class should be instantiated
- `inspector.inspect(source, profile=<profile>, **options)` should be called
- a returning value will be a report dictionary

#### Dataset

Goodtables support different sources for an inspection. But it should be convertable to dataset presented on a figure 1. Details will be explained in the next sections:

![Dataset](files/dataset.png)

#### Report

As a result of inspection goodtables returns a report dictionary. It includes valid flag, count of errors, list of reports per table including errors etc. See example above for an instance.  A report structure and all errors are standartised and described in **data quality spec**:

> https://github.com/roll/goodtables-next/tree/master/goodtables/spec.json

Report errors are categorized by type:

- source - data can't be loaded or parsed
- structure - general tabular errors like duplicate headers
- schema - error of checks against JSON Table Schema

Report errors are categorized by context:

- dataset - the whole dataset errors like invalid datapackage
- table - the whole table errors like bad encoding
- head - headers errors
- body - contents errors

### Profiles

Table is a main inspection object in goodtables. The simplest option is to pass to `Inspector.inspect` path and other options for one table (see example above). But when multitable parallized inspection is needed profiles could be used to process a dataset.

Let's see how to inspect a datapackage:

```python
from goodtables import Inspector

inspector = Inspector()
inspector.inspect('datapackage.json', profile='datapackage')
```

A profile proceses passed source and options and return it as a dataset containing tables with extras for the following inspection.

#### Builtin profiles

Goodtables by default supports the following profiles:

- table
- datapackage
- ckan

#### Custom profiles

> Provisional API not following SemVer. If you use it as a part of other program please pin concrete `goodtables` version to your requirements file.

To register a custom profile user could use a `profile(name)` decorator. This way the builtin profile could be overriden or could be added a custom profile.

```python
from jsontableschema import Table
from goodtables import Inspector, profile

@profile('custom-profile')
def custom_profile(source, **options):
    dataset = []
    for table in source:
        dataset.append({
            'table': Table(...),
            'extra': {...},
        })
    return dataset

inspector = Inspector()
inspector.inspect(source, profile='custom-profile')
```

See builtin profiles to learn more about the dataset extration protocol.

### Checks

Check is a main inspection actor in goodtables. Every check is associated with a specification error. Checking order is the same as order of errors in the specification.  List of checks could be customized using inspector's `checks` argument. Let's explore options on an example:

```python
inspector = Inspector(checks='all/structure/schema') # preset
inspector = Inspector(checks={'bad-headers': False}) # exclude
inspector = Inspector(checks={'bad-headers': True}) # cherry-pick
```

Check gets input data from framework based on context (e.g. `columns` and `sample` for `head` context) and returns list of corresponding errors.

#### Buitin checks

Goodtables by default supports the following checks:

 - [check for every error from the specification]

#### Custom checks

> Provisional API not following SemVer. If you use it as a part of other program please pin concrete `goodtables` version to your requirements file.

To register a custom check user could use a `check(error)` decorator. This way the builtin check could be overriden or could be added a check for a custom error:

```python
from goodtables import Inspector, check

# For builtin error
@check('blank-row')
# For custom error (use after/before argument to set an insertion position)
@check({'code': custom-error', 'type': 'structure', 'context': 'body'}, after='blank-row')
def custom_check(row_number, columns,  sample):
    errors = []
    for column in columns:
        errors.append({
            'message': 'Custom error',
            'row-number': row_number,
            'column-number': column['number'],
        })
    return errors

inspector = Inspector(checks='structure', custom_errors=[...])
```
See builtin checks to learn more about checking protocol.

### CLI

> Provisional API not following SemVer. If you use it as a part of other program please pin concrete `goodtables` version to your requirements file.

All common goodtables tasks could be done using a command-line interface (command per profile):

```
$ python -m goodtables.cli
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --json
  --table-limit INTEGER
  --row-limit INTEGER
  --error-limit INTEGER
  --order-fields
  --infer-fields
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

## API Reference

### Snapshot

```
Inspector(checks='all',
          table_limit=10,
          row_limit=1000,
          error_limit=1000,
          order_fields=False,
          infer_fields=False,
          ~custom_errors=[])
    inspect(source, profile='table', **options)
~@profile(name)
~@check(name)
exceptions
~cli
```

### Detailed

- [Docstrings](https://github.com/frictionlessdata/goodtables-py/tree/master/goodtables)
- [Changelog](https://github.com/frictionlessdata/goodtables/commits/master)

## Contributing

Please read the contribution guideline:

[How to Contribute](CONTRIBUTING.md)

Thanks!
