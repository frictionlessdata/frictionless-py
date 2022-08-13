# Baseline Check

The Baseline Check is always enabled. It makes various small checks that reveal a great deal of tabular errors. There is a `report.tasks[].scope` property to check which exact errors have been checked for:

> Download [`capital-invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-invalid.csv) to reproduce the examples (right-click and "Save link as")..

```python title="Python"
from pprint import pprint
from frictionless import validate

report = validate('capital-invalid.csv')
pprint(report.task.scope)
```
```
['hash-count-error',
 'byte-count-error',
 'field-count-error',
 'row-count-error',
 'blank-header',
 'extra-label',
 'missing-label',
 'blank-label',
 'duplicate-label',
 'incorrect-label',
 'blank-row',
 'primary-key-error',
 'foreign-key-error',
 'extra-cell',
 'missing-cell',
 'type-error',
 'constraint-error',
 'unique-error']
```

The Baseline Check is incorporated into base Frictionless classes as though Resource, Header, and Row. There is no exact order in which those errors are revealed as it's highly optimized. One should consider the Baseline Check as one unit of validation.
