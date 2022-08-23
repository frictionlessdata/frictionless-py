# Any Field

## Overview

AnyField provides an ability to skip any cell parsing. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#any).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], [1], ['1']]
rows = extract(data, schema=Schema(fields=[fields.AnyField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.AnyField
```
