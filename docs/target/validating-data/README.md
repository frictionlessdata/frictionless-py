# Validating Data

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1cJSZlG_v6OI3I2FtnXdKOSPjhwZNjMK1)



Tabular data validation is a process of identifying tabular problems that have place in your data for further correction. Let's explore how Frictionless helps to achieve these tasks using an invalid data table example:


```bash
! pip install frictionless
```


```bash
! wget -q -O capital.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-invalid.csv
! cat capital.csv
```

    id,name,name
    1,London,Britain
    2,Berlin,Germany
    3,Paris,France
    4,Madrid,Spain
    5,Rome,Italy
    6,Zagreb,Croatia
    7,Athens,Greece
    8,Vienna,Austria
    8,Warsaw

    x,Tokio,Japan,review


Using the command-line interface we can validate this file. Frictionless provides comprehensive error details so it's self-explanatory. Continue reading to learn the validation process in-details.


```bash
! frictionless validate capital.csv
```

    [invalid] capital.csv

      row    field  code              message
    -----  -------  ----------------  --------------------------------------------------------------------------------------------------------------------
                 3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"
       10        3  missing-cell      Row at position "10" has a missing cell in field "name2" at position "3"
       11           blank-row         Row at position "11" is completely blank
       12        4  extra-cell        Row at position "12" has an extra value in field at position "4"
       12        1  type-error        The cell "x" in row at position "12" and field "id" at position "1" has incompatible type: type is "integer/default"


## Validate Functions

The high-level interface for validating data provided by Frictionless is a set of `validate` functions:
- `validate`: it will detect the source type and validate data accordingly
- `validate_schema`: it validates a schema's metadata
- `validate_resource`: it validates a resource's data and metadata
- `validate_package`: it validates a package's data and metadata
- `validate_inquiery`: it validates a special `Inquiery` object which represents a validation task instruction
- `validate_table`: it validates a table

In command-line, there is only 1 command but there is a flag to adjust the behavior:

```bash
$ frictionless validate
$ frictionless validate --source-type schema
$ frictionless validate --source-type resource
$ frictionless validate --source-type package
$ frictionless validate --source-type inquiry
$ frictionless validate --source-type table
```

### Validating Schema

The `validate_schema` function is the only function validating solely metadata. Let's create a invalid table schema:


```python
from frictionless import Schema

schema = Schema()
schema.fields = {} # must be a list
schema.to_yaml('invalid.schema.yaml')
```

And validate it using the command-line interface:


```bash
! frictionless validate invalid.schema.yaml
```

    [invalid] invalid.schema.yaml

    code          message
    ------------  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    schema-error  The data source could not be successfully described by the invalid Table Schema: "{} is not of type 'array'" at "fields" in metadata and at "properties/fields/type" in profile


Schema validation can be very useful when you work with different classes of tables and create schemas for them. Using this function you can ensure that the metadata is valid.

### Validating Resource

As it was shown in the "Describing Data" guide a resource is a container having both metadata and data. We need to create a resource descriptor to validate it:


```bash
! frictionless describe capital.csv --json > capital.resource.json
```

Let's now use the command-line interface to ensure that we are getting the same result as we had withouth using a resource:


```bash
! frictionless validate capital.resource.json
```

    [invalid] capital.csv

      row    field  code              message
    -----  -------  ----------------  --------------------------------------------------------------------------------------------------------------------
                 3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"
       10        3  missing-cell      Row at position "10" has a missing cell in field "name2" at position "3"
       11           blank-row         Row at position "11" is completely blank
       12        4  extra-cell        Row at position "12" has an extra value in field at position "4"
       12        1  type-error        The cell "x" in row at position "12" and field "id" at position "1" has incompatible type: type is "integer/default"


Okay, why do we need to use a resource descriptor if the result is the same? The reason is metadata + data packaging. Let's extend our resource descriptor:


```python
from frictionless import describe

resource = describe('capital.csv')
resource['bytes'] = 100 # wrong
resource['hash'] = 'ae23c74693ca2d3f0e38b9ba3570775b' # wrong
resource.to_yaml('capital.resource.yaml')
```

We have added a few bad metrics to our resource descriptor. The validation below reports it in addition to all the errors we had before. This example is showing how concepts like Data Resource can be extremely useful when working with data.


```bash
! frictionless validate capital.resource.yaml
```

    [invalid] capital.csv

      row    field  code              message
    -----  -------  ----------------  -----------------------------------------------------------------------------------------------------------------------------------------------------------------
                 3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"
       10        3  missing-cell      Row at position "10" has a missing cell in field "name2" at position "3"
       11           blank-row         Row at position "11" is completely blank
       12        4  extra-cell        Row at position "12" has an extra value in field at position "4"
       12        1  type-error        The cell "x" in row at position "12" and field "id" at position "1" has incompatible type: type is "integer/default"
                    checksum-error    The data source does not match the expected checksum: expected hash in md5 is "ae23c74693ca2d3f0e38b9ba3570775b" and actual is "dcdeae358cfd50860c18d953e021f836"
                    checksum-error    The data source does not match the expected checksum: expected bytes count is "100" and actual is "171"


### Validating Package

A package is a set of resources + additional metadata. To showcase a package validation we need one more tabular file:


```bash
! wget -q -O capital-valid.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv
! cat capital-valid.csv
```

    id,name
    1,London
    2,Berlin
    3,Paris
    4,Madrid
    5,Rome


Let's describe and validate a package:


```bash
! frictionless describe capital*.csv --json > capital.package.json
! frictionless validate capital.package.json
```

    [invalid] capital.csv

      row    field  code              message
    -----  -------  ----------------  --------------------------------------------------------------------------------------------------------------------
                 3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"
       10        3  missing-cell      Row at position "10" has a missing cell in field "name2" at position "3"
       11           blank-row         Row at position "11" is completely blank
       12        4  extra-cell        Row at position "12" has an extra value in field at position "4"
       12        1  type-error        The cell "x" in row at position "12" and field "id" at position "1" has incompatible type: type is "integer/default"

    [valid] capital-valid.csv


As we can see, the result is pretty straight-forward and expected: we have one invalid resource and one valid. One important note regarding the package validation: if there are more than one resource, it will use multiprocessing to speed up the process

### Validating Inquiry

The Inquiry gives you an ability to create arbitrary validation jobs containing a set of individual validation taks. Let's create an inquiry that includes an individual file validation and a resource validation:


```python
from frictionless import Inquiry

inquiry = Inquiry({'tasks': [
  {'source': 'capital-valid.csv'},
  {'source': 'capital.resource.json'},
]})
inquiry.to_yaml('capital.inquiry.yaml')
```

Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions have. As usual, let' run validation:


```bash
! frictionless validate capital.inquiry.yaml
```

    [valid] capital-valid.csv
    [invalid] capital.csv

      row    field  code              message
    -----  -------  ----------------  --------------------------------------------------------------------------------------------------------------------
                 3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"
       10        3  missing-cell      Row at position "10" has a missing cell in field "name2" at position "3"
       11           blank-row         Row at position "11" is completely blank
       12        4  extra-cell        Row at position "12" has an extra value in field at position "4"
       12        1  type-error        The cell "x" in row at position "12" and field "id" at position "1" has incompatible type: type is "integer/default"


At first sight, it's no clear why such a construct exists but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power. Last but not least, the Inquiry will use multiprocessing if there are more than 1 task provided.

### Validating Table

All the functions above except for `validate_schema` are just wrappers over the `validate_table` function. Below we will be talking a lot about the table validation so here will just provide a simple example:


```bash
! frictionless validate capital.csv --pick-errors duplicate-header
```

    [invalid] capital.csv

    row      field  code              message
    -----  -------  ----------------  ------------------------------------------------------------------------------------------------
                 3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"


Please keep reading to learn about the table validation in-detail.

## Validation Options

Let's overview options that the described `validate` functions accept:

**Schema/Inquiry**

The `validate_schema` and `validate_inquiry` don't accept any options in addition to `source`.

**Resource/Package**

The Resource and Package incapsulate most of information within their descriptor so the amount of additional options is really limited:
- `basepath`: base path for a resource/package
- `noinfer`: a flag disabling an infer function call

**Table**

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

report = validate('capital.csv', pick_errors=['duplicate-header'])
pprint(report)
```

    {'errors': [],
     'stats': {'errors': 1, 'tables': 1},
     'tables': [{'compression': 'no',
                 'compressionPath': '',
                 'dialect': {},
                 'encoding': 'utf-8',
                 'errors': [{'cell': 'name',
                             'cells': ['id', 'name', 'name'],
                             'code': 'duplicate-header',
                             'description': 'Two columns in the header row have '
                                            'the same value. Column names should '
                                            'be unique.',
                             'fieldName': 'name2',
                             'fieldNumber': 3,
                             'fieldPosition': 3,
                             'message': 'Header "name" in field at position "3" is '
                                        'duplicated to header in another field: at '
                                        'position "2"',
                             'name': 'Duplicate Header',
                             'note': 'at position "2"',
                             'tags': ['#head', '#structure']}],
                 'format': 'csv',
                 'hashing': 'md5',
                 'header': ['id', 'name', 'name'],
                 'partial': False,
                 'path': 'capital.csv',
                 'query': {},
                 'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                       {'name': 'name', 'type': 'string'},
                                       {'name': 'name2', 'type': 'string'}]},
                 'scheme': 'file',
                 'scope': ['duplicate-header'],
                 'stats': {'bytes': 171,
                           'errors': 1,
                           'hash': 'dcdeae358cfd50860c18d953e021f836',
                           'rows': 11},
                 'time': 0.011,
                 'valid': False}],
     'time': 0.011,
     'valid': False,
     'version': '0.6.0'}


As we can see, there are a lot of information; you can find its details description in "API Reference". Errors are groupped by tables; for some validation there are can be dozens of tables. Let's use the `report.flatten` function to simplify errors representation:


```python
from frictionless import validate

report = validate('capital.csv', pick_errors=['duplicate-header'])
pprint(report.flatten(['rowPosition', 'fieldPosition', 'code', 'message']))
```

    [[None,
      3,
      'duplicate-header',
      'Header "name" in field at position "3" is duplicated to header in another '
      'field: at position "2"']]


In some situation, an error can't be associated with a table; then it goes to the top-level `report.errors` property:


```python
from frictionless import validate_schema

report = validate_schema('bad.json')
pprint(report)
```

    {'errors': [{'code': 'schema-error',
                 'description': 'Provided schema is not valid.',
                 'message': 'The data source could not be successfully described '
                            'by the invalid Table Schema: canot extract metadata '
                            '"bad.json" because "[Errno 2] No such file or '
                            'directory: \'bad.json\'"',
                 'name': 'Schema Error',
                 'note': 'canot extract metadata "bad.json" because "[Errno 2] No '
                         'such file or directory: \'bad.json\'"',
                 'tags': ['#table', '#schema']}],
     'stats': {'errors': 1, 'tables': 0},
     'tables': [],
     'time': 0.0,
     'valid': False,
     'version': '0.6.0'}


## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tables[].errors` properties that can contain the Error object. Let's explore it:


```python
from frictionless import validate

report = validate('capital.csv', pick_errors=['duplicate-header'])
error = report.table.error # it's only available for 1 table / 1 error sitution
print(f'Code: "{error.code}"')
print(f'Name: "{error.name}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```

    Code: "duplicate-header"
    Name: "Duplicate Header"
    Tags: "['#head', '#structure']"
    Note: "at position "2""
    Message: "Header "name" in field at position "3" is duplicated to header in another field: at position "2""
    Description: "Two columns in the header row have the same value. Column names should be unique."


Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-header` error:


```python
from frictionless import validate

report = validate('capital.csv', pick_errors=['duplicate-header'])
error = report.table.error # it's only available for 1 table / 1 error sitution
pprint(error)
```

    {'cell': 'name',
     'cells': ['id', 'name', 'name'],
     'code': 'duplicate-header',
     'description': 'Two columns in the header row have the same value. Column '
                    'names should be unique.',
     'fieldName': 'name2',
     'fieldNumber': 3,
     'fieldPosition': 3,
     'message': 'Header "name" in field at position "3" is duplicated to header in '
                'another field: at position "2"',
     'name': 'Duplicate Header',
     'note': 'at position "2"',
     'tags': ['#head', '#structure']}


Please explore "Errors Reference" to learn about all the avialble errors and their properties.

## Errors Options

We have already seen a few mentions of error options like `pick_errors`. Let's take a look at all of them. These options are similiar to the `extract`'s counterparts for fields and rows.

**Pick/Skip Errors**

We can pick or skip errors providing a list of error codes. For example:


```python
from frictionless import validate

report1 = validate('capital.csv', pick_errors=['duplicate-header'])
report2 = validate('capital.csv', skip_errors=['duplicate-header'])
pprint(report1.flatten(['rowPosition', 'fieldPosition', 'code']))
pprint(report2.flatten(['rowPosition', 'fieldPosition', 'code']))
```

    [[None, 3, 'duplicate-header']]
    [[10, 3, 'missing-cell'],
     [11, None, 'blank-row'],
     [12, 4, 'extra-cell'],
     [12, 1, 'type-error']]


It's also possible to use error tags (for more information please consult with "Errors Reference"):


```python
from frictionless import validate

report1 = validate('capital.csv', pick_errors=['#head'])
report2 = validate('capital.csv', skip_errors=['#body'])
pprint(report1.flatten(['rowPosition', 'fieldPosition', 'code']))
pprint(report2.flatten(['rowPosition', 'fieldPosition', 'code']))
```

    [[None, 3, 'duplicate-header']]
    [[None, 3, 'duplicate-header']]


**Limit Errors**

This option is self-explanatory and can be used when you need to "fail fast" or get a limited amount of errors:


```python
from frictionless import validate

report = validate('capital.csv', limit_errors=1)
pprint(report.flatten(['rowPosition', 'fieldPosition', 'code']))
```

    [[None, 3, 'duplicate-header']]


## Memory Options

Frictionless is a streaming engine; usually it's possible to validate terrabytes of data with basically O(1) memory consumption. For some validation, it's not the case because Frctionless needs to buffer some cells e.g. to checks uniqueness. Here memory management can be handy.

**Limit Memory**

Default memory limit is 1000MB. You can adjust it based on your exact use case. For example, if you're running Frictionless as an API server you might reduce the memory usage. If a validation hits the limit it will not raise of fail - it will return a report with a task error:


```python
from frictionless import validate

source = lambda: ([integer] for integer in range(1, 100000000))
schema = {"fields": [{"name": "integer", "type": "integer"}], "primaryKey": "integer"}
report = validate(source, headers=False, schema=schema, limit_memory=50)
print(report.flatten(["code", "note"]))

```

    [['task-error', 'exceeded memory limit "50MB"']]


## Checks Options

Ther are two check options: `checksum` and `extra_checks`. The first allows to stricten a baseline validation white the latter is used to enforce additional checks.

**Checksum**

We can provide a hash string, the amount of bytes, and the amount of rows. Frictionless will ensure as a part of a validation that the actual values match the expected ones. Let's show for the hash:


```python
from frictionless import validate

report = validate('capital.csv', checksum={'hash': 'bad'}, pick_errors=['#checksum'])
print(report.flatten(["code", "note"]))
```

    [['checksum-error', 'expected hash in md5 is "bad" and actual is "dcdeae358cfd50860c18d953e021f836"']]


The same can be show for the bytes and rows:


```python
from frictionless import validate

report = validate('capital.csv', checksum={'bytes': 10, 'rows': 10}, pick_errors=['#checksum'])
pprint(report.flatten(["code", "note"]))
```

    [['checksum-error', 'expected bytes count is "10" and actual is "171"'],
     ['checksum-error', 'expected rows count is "10" and actual is "11"']]


**Extra Checks**

It's possible to provide a list of extra checks where individual checks are in the form of:
- a string: `check-name`
- a list: `['check-name', {'option1': 'value1'}]`

It's also possible to use a `Check` subclass instead of name which will be shown in the "Custom Checks" section. Let's have a loot at an example:


```python
from frictionless import validate

report = validate('capital.csv', extra_checks=[('sequential-value', {'fieldName': 'id'})])
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "note"]))
```

    [[None, 3, 'duplicate-header', 'at position "2"'],
     [10, 3, 'missing-cell', ''],
     [10, 1, 'sequential-value', 'the value is not sequential'],
     [11, None, 'blank-row', ''],
     [12, 4, 'extra-cell', ''],
     [12, 1, 'type-error', 'type is "integer/default"']]


See the sections below for a list of available checks.

## Baseline Check

By default, Frictionless runs only the Baseline Check but includes vairous smaller checks revealing a great deal of tabular errors. There is a `report.tables[].scope` property to check what exact errors it have been checked for:


```python
from frictionless import validate

report = validate('capital.csv')
pprint(report.table.scope)
```

    ['dialect-error',
     'schema-error',
     'field-error',
     'extra-header',
     'missing-header',
     'blank-header',
     'duplicate-header',
     'non-matching-header',
     'extra-cell',
     'missing-cell',
     'blank-row',
     'type-error',
     'constraint-error',
     'unique-error',
     'primary-key-error',
     'foreign-key-error',
     'checksum-error']


## Heuristic Checks

There is a group of checks that indicate probable errors. You need to use the `extra_checks` argument of the `validate` function to active one or more of these checks.



**Duplicate Row**

This check is self-explanatory. You need to take into account that checking for duplicate rows can lean to high memory consumption on big files. Here is an example:


```python
from pprint import pprint
from frictionless import validate

source = 'header\nvalue\nvalue'
report = validate(source, scheme='text', format='csv', extra_checks=['duplicate-row'])
pprint(report.flatten(['code', 'message']))
```

    [['duplicate-row',
      'Row at position 3 is duplicated: the same as row at position "2"']]


**Deviated Value**

This checks uses the extranal `statistics` package to checks a field for deviations. For example:


```python
    from pprint import pprint
    from frictionless import validate

    source = [["temperature"], [1], [-2], [7], [0], [1], [2], [5], [-4], [1000], [8], [3]]
    report = validate(source, extra_checks=[("deviated-value", {"fieldName": "temperature"})])
    pprint(report.flatten(["code", "message"]))

```

    [['deviated-value',
      'There is a possible error because the value is deviated: value "1000" in '
      'row at position "10" and field "temperature" is deviated "[-809.88, '
      '995.52]"']]


**Truncated Value**

Sometime during the explort from a database or another storage, data values can be truncated. This check tries to detect it. Let's explore some trunctation indicators:


```python
from pprint import pprint
from frictionless import validate

source = [["int", "str"], ["a" * 255, 32767], ["good", 2147483647]]
report = validate(source, extra_checks=["truncated-value"],)
pprint(report.flatten(["code", "message"]))
```

    [['truncated-value',
      'The cell '
      'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa '
      'in row at position 2 and field int at position 1 has an error: value  is '
      'probably truncated'],
     ['truncated-value',
      'The cell 32767 in row at position 2 and field str at position 2 has an '
      'error: value  is probably truncated'],
     ['truncated-value',
      'The cell 2147483647 in row at position 3 and field str at position 2 has an '
      'error: value  is probably truncated']]


## Regulation Checks

In countrary to probably checks, regulation checks gives you an ability to provide additional rules for your data. Use the `extra_checks` argument of the `validate` function to active one or more of these checks.

**Blacklisted Value**

This check ensures that some field doesn't have any blacklisted values. For example:


```python
from pprint import pprint
from frictionless import validate

source = 'header\nvalue1\nvalue2'
extra_checks = [('blacklisted-value', {'fieldName': 'header', 'blacklist': ['value2']})]
report = validate(source, scheme='text', format='csv', extra_checks=extra_checks)
pprint(report.flatten(['code', 'message']))
```

    [['blacklisted-value',
      'The cell value2 in row at position 3 and field header at position 1 has an '
      'error: blacklisted values are "[\'value2\']"']]


**Sequential Value**

This check gives us an opportunity to validate sequential fields like primary keys or other similiar data. It doesn't need to start from 0 or 1. We're providing a field name:


```python
from pprint import pprint
from frictionless import validate

source = 'header\n2\n3\n5'
extra_checks = [('sequential-value', {'fieldName': 'header'})]
report = validate(source, scheme='text', format='csv', extra_checks=extra_checks)
pprint(report.flatten(['code', 'message']))
```

    [['sequential-value',
      'The cell 5 in row at position 4 and field header at position 1 has an '
      'error: the value is not sequential']]


**Row Constraint**

This checks is the most powerful one as it uses the external `simpleeval` package allowing to evalute arbitrary python expressions on data rows. Let's show on an example:


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

    [['row-constraint',
      'The row at position 4 has an error: the row constraint to conform is '
      '"salary == bonus * 5"']]


## Custom Checks

There are many cases when built-in Frictionless' checks are not enough. It can be a business logic rule or specific quality requirement to the data. With Frictionless it's very easy to use your own custom checks. Let's see on an example:


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

    [[3, 1, 'cell-error', 'number 2 is forbidden!']]


Usualy, it also makes sense to create a custom error for your custom check. The Check class provides other useful methods like `validate_header` etc. Please read "API Reference" to learn it in details.