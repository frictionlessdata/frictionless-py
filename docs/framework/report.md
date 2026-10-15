---
script:
  basepath: data
---

# Report Class

## Validation Report

All the `validate` functions return a Validation Report. It is a unified object containing
information about a validation run: whether the data is valid, validation statistics, top-level
metadata errors, and task-level errors for each validated resource. Let's explore a report:

```python script tabs=Python
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
print(report)
```

The main report fields are:

- `report.valid`: whether the whole validation run passed.
- `report.stats`: aggregate counts such as tasks, errors, warnings, and elapsed seconds.
- `report.errors`: top-level errors that are not associated with a specific validation task.
- `report.tasks`: task reports, usually one per validated resource.

Task reports contain their own `valid`, `place`, `labels`, `stats`, `warnings`, and `errors`
properties. For example, package and inquiry validation can produce multiple tasks.

Let's use the `report.flatten` function to simplify error representation:

```python script tabs=Python
from pprint import pprint
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
pprint(report.flatten(["taskNumber", "rowNumber", "fieldNumber", "code", "message"]))
```

`flatten()` returns a list of rows using the requested property names. It includes top-level
`report.errors` and all `report.tasks[].errors`; `taskNumber` is added for task-level errors.

In some situations, an error can't be associated with a validation task; then it goes to the
top-level `report.errors` property:

```python script tabs=Python
from frictionless import validate

report = validate("bad.json", type="schema")
print(report)
```

For convenience, `report.task` is available when the report has exactly one task, and
`report.error` is available when the report has exactly one error. Similarly, `task.error` is
available when a task has exactly one error.

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and
`report.tasks[].errors` properties that can contain Error objects. Let's explore one:

```python script tabs=Python
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
error = report.error  # available only for single-error reports
print(f'Type: "{error.type}"')
print(f'Title: "{error.title}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```

Above, we have listed universal error properties. Depending on the type of error, there can be
additional properties. For example, for our `duplicate-label` error:

```python script tabs=Python
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
error = report.error
print(error)
```

Some common location properties are:

- `rowNumber`: the row where the error occurred.
- `fieldName` / `fieldNumber`: the field where the error occurred, for field-specific errors.
- `cells`: the full row values at the point where the row-level or cell-level error was detected.
- `cell`: the specific cell value that failed, for cell-level errors.

This means that `cells` provides row context, while `cell` points to the individual problematic
value when the error is tied to a specific field. For example, an `extra-cell` error includes both
the complete row in `cells` and the extra value in `cell`.

Please explore the [Errors Reference](../errors/cell.html) to learn about all the available
errors and their properties.

## Reference

```yaml reference
references:
  - frictionless.Report
  - frictionless.ReportTask
```
