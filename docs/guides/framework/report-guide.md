---
title: Report Guide
---

## Validation Report

All the `validate` functions return the Validation Report. It's an unified object containing information about a validation: source details, found error, etc. Let's explore a report:

```python goodread title="Python"
from pprint import pprint
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-label'])
pprint(report)
```
```
{'errors': [],
 'stats': {'errors': 1, 'tasks': 1},
 'tasks': [{'errors': [{'code': 'duplicate-label',
                        'description': 'Two columns in the header row have the '
                                       'same value. Column names should be '
                                       'unique.',
                        'fieldName': 'name2',
                        'fieldNumber': 3,
                        'fieldPosition': 3,
                        'label': 'name',
                        'labels': ['id', 'name', 'name'],
                        'message': 'Label "name" in the header at position "3" '
                                   'is duplicated to a label: at position "2"',
                        'name': 'Duplicate Label',
                        'note': 'at position "2"',
                        'rowPositions': [1],
                        'tags': ['#table', '#header', '#label']}],
            'partial': False,
            'resource': {'encoding': 'utf-8',
                         'format': 'csv',
                         'hashing': 'md5',
                         'name': 'capital-invalid',
                         'path': 'data/capital-invalid.csv',
                         'profile': 'tabular-data-resource',
                         'schema': {'fields': [{'name': 'id',
                                                'type': 'integer'},
                                               {'name': 'name',
                                                'type': 'string'},
                                               {'name': 'name2',
                                                'type': 'string'}]},
                         'scheme': 'file',
                         'stats': {'bytes': 171,
                                   'fields': 3,
                                   'hash': 'dcdeae358cfd50860c18d953e021f836',
                                   'rows': 11}},
            'scope': ['duplicate-label'],
            'stats': {'errors': 1},
            'time': 0.026,
            'valid': False}],
 'time': 0.026,
 'valid': False,
 'version': '4.1.0'}
```

As we can see, there are a lot of information; you can find its details description in "API Reference". Errors are grouped by tables; for some validation there are can be dozens of tables. Let's use the `report.flatten` function to simplify errors representation:

```python goodread title="Python"
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-label'])
pprint(report.flatten(['rowPosition', 'fieldPosition', 'code', 'message']))
```
```
[[None,
  3,
  'duplicate-label',
  'Label "name" in the header at position "3" is duplicated to a label: at '
  'position "2"']]
```

In some situation, an error can't be associated with a table; then it goes to the top-level `report.errors` property:

```python goodread title="Python"
from frictionless import validate_schema

report = validate_schema('bad.json')
pprint(report)
```
```
{'errors': [{'code': 'schema-error',
             'description': 'Provided schema is not valid.',
             'message': 'Schema is not valid: cannot extract metadata '
                        '"bad.json" because "[Errno 2] No such file or '
                        'directory: \'bad.json\'"',
             'name': 'Schema Error',
             'note': 'cannot extract metadata "bad.json" because "[Errno 2] No '
                     'such file or directory: \'bad.json\'"',
             'tags': []}],
 'stats': {'errors': 1, 'tasks': 0},
 'tasks': [],
 'time': 0.0,
 'valid': False,
 'version': '4.1.0'}
```

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tables[].errors` properties that can contain the Error object. Let's explore it:

```python goodread title="Python"
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-label'])
error = report.task.error # it's only available for 1 table / 1 error sitution
print(f'Code: "{error.code}"')
print(f'Name: "{error.name}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```
```
Code: "duplicate-label"
Name: "Duplicate Label"
Tags: "['#table', '#header', '#label']"
Note: "at position "2""
Message: "Label "name" in the header at position "3" is duplicated to a label: at position "2""
Description: "Two columns in the header row have the same value. Column names should be unique."
```

Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-label` error:

```python goodread title="Python"
from frictionless import validate

report = validate('data/capital-invalid.csv', pick_errors=['duplicate-label'])
error = report.task.error # it's only available for 1 table / 1 error sitution
pprint(error)
```
```
{'code': 'duplicate-label',
 'description': 'Two columns in the header row have the same value. Column '
                'names should be unique.',
 'fieldName': 'name2',
 'fieldNumber': 3,
 'fieldPosition': 3,
 'label': 'name',
 'labels': ['id', 'name', 'name'],
 'message': 'Label "name" in the header at position "3" is duplicated to a '
            'label: at position "2"',
 'name': 'Duplicate Label',
 'note': 'at position "2"',
 'rowPositions': [1],
 'tags': ['#table', '#header', '#label']}
```

Please explore "Errors Reference" to learn about all the available errors and their properties.
