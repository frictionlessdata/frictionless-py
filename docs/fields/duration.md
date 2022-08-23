# Duration Field

## Overview

A duration of time. We follow the definition of XML Schema duration datatype directly
and that definition is implicitly inlined here. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#duration).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['P1Y']]
rows = extract(data, schema=Schema(fields=[fields.DurationField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.DurationField
```
