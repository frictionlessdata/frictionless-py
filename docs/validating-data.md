# Validating Data

Tabular data validation is a process of identifying tabular problems that occur in your data for further correction. Let's explore how Frictionless helps to achieve these tasks using an invalid data table example:

```python
! cat data/capital-invalid.csv
```

Using the command-line interface we can validate this file. Frictionless provides comprehensive error details so it's self-explanatory. Continue reading to learn the validation process in-details.

```python
! frictionless validate data/capital-invalid.csv
```

## Validate Functions

The high-level interface for validating data provided by Frictionless is a set of `validate` functions:
- `validate`: it will detect the source type and validate data accordingly
- `validate_schema`: it validates a schema's metadata
- `validate_resource`: it validates a resource's data and metadata
- `validate_package`: it validates a package's data and metadata
- `validate_inquiry`: it validates a special `Inquiry` object which represents a validation task instruction
- `validate_table`: it validates a table

In command-line, there is only 1 command but there is a flag to adjust the behavior:

```sh
$ frictionless validate
$ frictionless validate --source-type schema
$ frictionless validate --source-type resource
$ frictionless validate --source-type package
$ frictionless validate --source-type inquiry
$ frictionless validate --source-type table
```

### Validating Schema

The `validate_schema` function is the only function validating solely metadata. Let's create an invalid table schema:

```python
from frictionless import Schema

schema = Schema()
schema.fields = {} # must be a list
schema.to_yaml('tmp/invalid.schema.yaml')
```

And validate it using the command-line interface:

```python
! frictionless validate tmp/invalid.schema.yaml
```

Schema validation can be very useful when you work with different classes of tables and create schemas for them. Using this function you can ensure that the metadata is valid.

### Validating Resource

As it was shown in the "Describing Data" guide a resource is a container having both metadata and data. We need to create a resource descriptor to validate it:

```python
! frictionless describe data/capital-invalid.csv --json > tmp/capital.resource.json
```

Let's now use the command-line interface to ensure that we are getting the same result as we had without using a resource:

```python
! frictionless validate tmp/capital.resource.json --basepath .
```

Okay, why do we need to use a resource descriptor if the result is the same? The reason is metadata + data packaging. Let's extend our resource descriptor:

```python
from frictionless import describe

resource = describe('data/capital-invalid.csv')
resource['bytes'] = 100 # wrong
resource['hash'] = 'ae23c74693ca2d3f0e38b9ba3570775b' # wrong
resource.to_yaml('tmp/capital.resource.yaml')
```

We have added a few bad metrics to our resource descriptor. The validation below reports it in addition to all the errors we had before. This example is showing how concepts like Data Resource can be extremely useful when working with data.

```python
! frictionless validate tmp/capital.resource.yaml --basepath .
```

### Validating Package

A package is a set of resources + additional metadata. To showcase a package validation we need one more tabular file:

```python
! cat data/capital-valid.csv
```

Let's describe and validate a package:

```python
! frictionless describe data/capital-*id.csv --json > tmp/capital.package.json
! frictionless validate tmp/capital.package.json --basepath .
```

As we can see, the result is pretty straight-forward and expected: we have one invalid resource and one valid. One important note regarding the package validation: if there are more than one resource, it will use multiprocessing to speed up the process

### Validating Inquiry

The Inquiry gives you an ability to create arbitrary validation jobs containing a set of individual validation tasks. Let's create an inquiry that includes an individual file validation and a resource validation:

```python
from frictionless import Inquiry

inquiry = Inquiry({'tasks': [
  {'source': 'data/capital-valid.csv'},
  {'source': 'tmp/capital.resource.json', 'basepath': '.'},
]})
inquiry.to_yaml('tmp/capital.inquiry.yaml')
```

Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions have. As usual, let's run validation:

```python
! frictionless validate tmp/capital.inquiry.yaml
```

At first sight, it's not clear why such a construct exists but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power. Last but not least, the Inquiry will use multiprocessing if there are more than 1 task provided.

### Validating Table

All the functions above except for `validate_schema` are just wrappers over the `validate_table` function. Below we will be talking a lot about the table validation so here will just provide a simple example:

```python
! frictionless validate data/capital-invalid.csv --pick-errors duplicate-header
```

Please keep reading to learn about the table validation in-detail.

## Validation Options

Let's overview options that the described `validate` functions accept:

### Schema/Inquiry

The `validate_schema` and `validate_inquiry` don't accept any options in addition to `source`.

### Resource/Package

The Resource and Package encapsulate most of information within their descriptor so the amount of additional options is really limited:
- `basepath`: base path for a resource/package
- `noinfer`: a flag disabling an infer function call

### Table

The `validate_table` function accept most of the `describe/extract` function's options:

- File Details (see "Extracting Data")
- File Control (see "Extracting Data")
- Table Dialect (see "Extracting Data")
- Table Query (see "Extracting Data")
- Header Options (see "Extracting Data")
- Schema Options (see "Extracting Data")
- Integrity Options (see "Extracting Data")
- Infer Options (see "Describing Data")
- Errors Options
- Memory Options
- Checks Options

## Validation Report

All the `validate` functions return the Validation Report. It's an unified object containing information about a validation: source details, found error, etc. Let's explore a report:


```python
from pprint import pprint
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
pprint(report)
```

As we can see, there are a lot of information; you can find its details description in "API Reference". Errors are grouped by tables; for some validation exercises there can be dozens of tables. Let's use the `report.flatten` function to simplify errors representation:

```python
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
pprint(report.flatten(['rowPosition', 'fieldPosition', 'code', 'message']))
```

In some situations, an error can't be associated with a table; then it goes to the top-level `report.errors` property:

```python
from frictionless import validate_schema

report = validate_schema('bad.json')
pprint(report)
```

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tables[].errors` properties that can contain the Error object. Let's explore it:


```python
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
error = report.table.error # it's only available for 1 table / 1 error sitution
print(f'Code: "{error.code}"')
print(f'Name: "{error.name}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```

Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-header` error:

```python
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
error = report.table.error # it's only available for 1 table / 1 error sitution
pprint(error)
```

Please explore "Errors Reference" to learn about all the available errors and their properties.

## Errors Options

We have already seen a few mentions of error options like `pick_errors`. Let's take a look at all of them. These options are similiar to the `extract`'s counterparts for fields and rows.

### Pick/Skip Errors

We can pick or skip errors providing a list of error codes. For example:


```python
from frictionless import validate

report1 = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
report2 = validate('data/capital-invalid.csv', skip_errors=['duplicate-header'])
pprint(report1.flatten(['rowPosition', 'fieldPosition', 'code']))
pprint(report2.flatten(['rowPosition', 'fieldPosition', 'code']))
```

It's also possible to use error tags (for more information please consult with "Errors Reference"):

```python
from frictionless import validate

report1 = validate('data/capital-invalid.csv', pick_errors=['#head'])
report2 = validate('data/capital-invalid.csv', skip_errors=['#body'])
pprint(report1.flatten(['rowPosition', 'fieldPosition', 'code']))
pprint(report2.flatten(['rowPosition', 'fieldPosition', 'code']))
```

### Limit Errors

This option is self-explanatory and can be used when you need to "fail fast" or get a limited amount of errors:

```python
from frictionless import validate

report = validate('data/capital-invalid.csv', limit_errors=1)
pprint(report.flatten(['rowPosition', 'fieldPosition', 'code']))
```

## Memory Options

Frictionless is a streaming engine; usually it's possible to validate terabytes of data with basically O(1) memory consumption. For some validation, it's not the case because Frictionless needs to buffer some cells e.g. to checks uniqueness. Here memory management can be handy.

### Limit Memory

Default memory limit is 1000MB. You can adjust it based on your exact use case. For example, if you're running Frictionless as an API server you might reduce the memory usage. If a validation hits the limit it will not raise of fail - it will return a report with a task error:

```py
from frictionless import validate

source = lambda: ([integer] for integer in range(1, 100000000))
schema = {"fields": [{"name": "integer", "type": "integer"}], "primaryKey": "integer"}
report = validate(source, headers=False, schema=schema, limit_memory=50)
print(report.flatten(["code", "note"]))
# [['task-error', 'exceeded memory limit "50MB"']]
```

## Checks Options

There are two check options: `checksum` and `extra_checks`. The first allows to stricten a baseline validation while the latter is used to enforce additional checks.

### Checksum

We can provide a hash string, the amount of bytes, and the amount of rows. Frictionless will ensure as a part of a validation that the actual values match the expected ones. Let's show for the hash:


```python
from frictionless import validate

report = validate('data/capital-invalid.csv', checksum={'hash': 'bad'}, pick_errors=['#checksum'])
print(report.flatten(["code", "note"]))
```

The same can be shown for the bytes and rows:

```python
from frictionless import validate

report = validate('data/capital-invalid.csv', checksum={'bytes': 10, 'rows': 10}, pick_errors=['#checksum'])
pprint(report.flatten(["code", "note"]))
```

### Extra Checks

It's possible to provide a list of extra checks where individual checks are in the form of:
- a string: `check-name`
- a list: `['check-name', {'option1': 'value1'}]`

It's also possible to use a `Check` subclass instead of name which will be shown in the "Custom Checks" section. Let's have a look at an example:

```python
from frictionless import validate

report = validate('data/capital-invalid.csv', extra_checks=[('sequential-value', {'fieldName': 'id'})])
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "note"]))
```

See the sections below for a list of available checks.

## Baseline Check

By default, Frictionless runs only the Baseline Check but includes various smaller checks revealing a great deal of tabular errors. There is a `report.tables[].scope` property to check what exact errors it have been checked for:

```python
from frictionless import validate

report = validate('data/capital-invalid.csv')
pprint(report.table.scope)
```

## Heuristic Checks

There is a group of checks that indicate probable errors. You need to use the `extra_checks` argument of the `validate` function to activate one or more of these checks.

### Duplicate Row

This check is self-explanatory. You need to take into account that checking for duplicate rows can lead to high memory consumption on big files. Here is an example:


```python
from pprint import pprint
from frictionless import validate

source = 'header\nvalue\nvalue'
report = validate(source, scheme='text', format='csv', extra_checks=['duplicate-row'])
pprint(report.flatten(['code', 'message']))
```

### Deviated Value

This check uses the Python's builtin `statistics` module to check a field's data for deviations. By default, deviated values are outside of the average +- three standard deviations. Take a look at the [API Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/api-reference/README.md#deviatedvaluecheck) for more details about available options and default values. The exact algorithm can be found [here](https://github.com/frictionlessdata/frictionless-py/blob/7ae8bae9a9197adbfe443233a6bad8a94e065ece/frictionless/checks/heuristic.py#L94). For example:

```python
    from pprint import pprint
    from frictionless import validate

    source = [["temperature"], [1], [-2], [7], [0], [1], [2], [5], [-4], [1000], [8], [3]]
    report = validate(source, extra_checks=[("deviated-value", {"fieldName": "temperature"})])
    pprint(report.flatten(["code", "message"]))

```

### Truncated Value

Sometime during the explort from a database or another storage, data values can be truncated. This check tries to detect it. Let's explore some trunctation indicators:

```python
from pprint import pprint
from frictionless import validate

source = [["int", "str"], ["a" * 255, 32767], ["good", 2147483647]]
report = validate(source, extra_checks=["truncated-value"],)
pprint(report.flatten(["code", "message"]))
```

## Regulation Checks

In countrary to heuristic checks, regulation checks gives you an ability to provide additional rules for your data. Use the `extra_checks` argument of the `validate` function to active one or more of these checks.

### Blacklisted Value

This check ensures that some field doesn't have any blacklisted values. For example:

```python
from pprint import pprint
from frictionless import validate

source = 'header\nvalue1\nvalue2'
extra_checks = [('blacklisted-value', {'fieldName': 'header', 'blacklist': ['value2']})]
report = validate(source, scheme='text', format='csv', extra_checks=extra_checks)
pprint(report.flatten(['code', 'message']))
```

### Sequential Value

This check gives us an opportunity to validate sequential fields like primary keys or other similar data. It doesn't need to start from 0 or 1. We're providing a field name:

```python
from pprint import pprint
from frictionless import validate

source = 'header\n2\n3\n5'
extra_checks = [('sequential-value', {'fieldName': 'header'})]
report = validate(source, scheme='text', format='csv', extra_checks=extra_checks)
pprint(report.flatten(['code', 'message']))
```

### Row Constraint

This is the most powerful check as it uses the external `simpleeval` package allowing to evaluate arbitrary python expressions on data rows. Let's show on an example:

```python
from pprint import pprint
from frictionless import validate

source = [
  ["row", "salary", "bonus"],
  [2, 1000, 200],
  [3, 2500, 500],
  [4, 1300, 500],
  [5, 5000, 1000],
]
extra_checks=[("row-constraint", {"constraint": "salary == bonus * 5"})]
report = validate(source, extra_checks=extra_checks)
pprint(report.flatten(["code", "message"]))
```

## Custom Checks

There are many cases when Frictionless' built-in checks are not enough. It can be a business logic rule or specific quality requirement to the data. With Frictionless it's very easy to use your own custom checks. Let's see with an example:

```python
from pprint import pprint
from frictionless import validate, errors, Check

# Create check
class ForbidNumber(Check):
    def validate_row(self, row):
        if row['header'] == self['number']:
          note = f"number {self['number']} is forbidden!"
          yield errors.CellError.from_row(row, note=note, field_name='header')

# Validate table
source = 'header\n1\n2\n3'
extra_checks=[(ForbidNumber, {'number': 2})]
report = validate(source,  scheme='text', format='csv', extra_checks=extra_checks)
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "note"]))
```

Usually, it also makes sense to create a custom error for your custom check. The Check class provides other useful methods like `validate_header` etc. Please read "API Reference" to learn it in details.
