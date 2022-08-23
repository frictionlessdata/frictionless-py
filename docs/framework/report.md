---
script:
  basepath: data
---

# Report Class

## Validation Report

All the `validate` functions return the Validation Report. It's an unified object containing information about a validation: source details, found error, etc. Let's explore a report:

```python script tabs=Python
from frictionless import validate

report = validate('capital-invalid.csv', pick_errors=['duplicate-label'])
print(report)
```

As we can see, there are a lot of information; you can find its details description in "API Reference". Errors are grouped by tables; for some validation there are can be dozens of tables. Let's use the `report.flatten` function to simplify errors representation:

```python script tabs=Python
from pprint import pprint
from frictionless import validate

report = validate('capital-invalid.csv', pick_errors=['duplicate-label'])
pprint(report.flatten(['rowNumber', 'fieldNumber', 'code', 'message']))
```

In some situation, an error can't be associated with a table; then it goes to the top-level `report.errors` property:

```python script tabs=Python
from frictionless import validate

report = validate('bad.json', type='schema')
print(report)
```

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tables[].errors` properties that can contain the Error object. Let's explore it:

```python script tabs=Python
from frictionless import validate

report = validate('capital-invalid.csv', pick_errors=['duplicate-label'])
error = report.task.error # it's only available for 1 table / 1 error sitution
print(f'Type: "{error.type}"')
print(f'Title: "{error.title}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```

Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-label` error:

```python script tabs=Python
from frictionless import validate

report = validate('capital-invalid.csv', pick_errors=['duplicate-label'])
error = report.task.error # it's only available for 1 table / 1 error sitution
print(error)
```

Please explore "Errors Reference" to learn about all the available errors and their properties.

## Reference

```yaml reference
references:
  - frictionless.Report
  - frictionless.ReportTask
```
