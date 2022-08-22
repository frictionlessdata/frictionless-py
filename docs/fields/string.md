# String Field

## Overview

The field contains strings, that is, sequences of characters. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#string).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['value']]
rows = extract(data, schema=Schema(fields=[fields.StringField(name='name')]))
print(rows)
```

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=StringField
name: frictionless.fields.StringField
```
