# Number Field

## Overview

The field contains numbers of any kind including decimals. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#number).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['1.1'], ['2.2'], ['3.3']]
rows = extract(data, schema=Schema(fields=[fields.NumberField(name='name')]))
print(rows)
```

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=NumberField
name: frictionless.fields.NumberField
```
