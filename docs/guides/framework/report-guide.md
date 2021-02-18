---
title: Report Guide
---

## Validation Report

All the `validate` functions return the Validation Report. It's an unified object containing information about a validation: source details, found error, etc. Let's explore a report:

```python title="Python"
from pprint import pprint
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
pprint(report)
```
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
             'path': 'data/capital-invalid.csv',
             'query': {},
             'schema': {'fields': [{'name': 'id', 'type': 'integer'},
                                   {'name': 'name', 'type': 'string'},
                                   {'name': 'name2', 'type': 'string'}]},
             'scheme': 'file',
             'scope': ['duplicate-header'],
             'stats': {'bytes': 171,
                       'errors': 1,
                       'fields': 3,
                       'hash': 'dcdeae358cfd50860c18d953e021f836',
                       'rows': 11},
             'time': 0.019,
             'valid': False}],
 'time': 0.019,
 'valid': False,
 'version': '3.38.1'}
```

As we can see, there are a lot of information; you can find its details description in "API Reference". Errors are grouped by tables; for some validation there are can be dozens of tables. Let's use the `report.flatten` function to simplify errors representation:

```python title="Python"
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
pprint(report.flatten(['rowPosition', 'fieldPosition', 'code', 'message']))
```
```
[[None,
  3,
  'duplicate-header',
  'Header "name" in field at position "3" is duplicated to header in another '
  'field: at position "2"']]
```

In some situation, an error can't be associated with a table; then it goes to the top-level `report.errors` property:

```python title="Python"
from frictionless import validate_schema

report = validate_schema('bad.json')
pprint(report)
```
```
{'errors': [{'code': 'schema-error',
             'description': 'Provided schema is not valid.',
             'message': 'The data source could not be successfully described '
                        'by the invalid Table Schema: cannot extract metadata '
                        '"bad.json" because "[Errno 2] No such file or '
                        'directory: \'bad.json\'"',
             'name': 'Schema Error',
             'note': 'cannot extract metadata "bad.json" because "[Errno 2] No '
                     'such file or directory: \'bad.json\'"',
             'tags': ['#table', '#schema']}],
 'stats': {'errors': 1, 'tables': 0},
 'tables': [],
 'time': 0.0,
 'valid': False,
 'version': '3.38.1'}
```

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tables[].errors` properties that can contain the Error object. Let's explore it:

```python title="Python"
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
```
Code: "duplicate-header"
Name: "Duplicate Header"
Tags: "['#head', '#structure']"
Note: "at position "2""
Message: "Header "name" in field at position "3" is duplicated to header in another field: at position "2""
Description: "Two columns in the header row have the same value. Column names should be unique."
```

Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-header` error:


```python title="Python"
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-header'])
error = report.table.error # it's only available for 1 table / 1 error sitution
pprint(error)
```
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
```

Please explore "Errors Reference" to learn about all the available errors and their properties.
