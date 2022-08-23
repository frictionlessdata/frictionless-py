---
script:
  basepath: data
---

# Baseline Check

## Overview

The Baseline Check is always enabled. It makes various small checks that reveal a great deal of tabular errors. You can create an empty `Checklist` to see the baseline check scope:

> Download [`capital-invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/capital-invalid.csv) to reproduce the examples (right-click and "Save link as")..

```python script tabs=Python
from pprint import pprint
from frictionless import Checklist, validate

checklist = Checklist()
pprint(checklist.scope)
report = validate('capital-invalid.csv')  # we don't pass the checklist as the empty one is default
pprint(report.flatten(['type', 'message']))
```

The Baseline Check is incorporated into base Frictionless classes as though Resource, Header, and Row. There is no exact order in which those errors are revealed as it's highly optimized. One should consider the Baseline Check as one unit of validation.

## Reference

```yaml reference
references:
  - frictionless.checks.baseline
```
