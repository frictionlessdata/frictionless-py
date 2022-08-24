# Boolean Field

## Overview

The field contains boolean (true/false) data.

In the physical representations of data where boolean values are represented with strings, the values set in trueValues and falseValues are to be cast to their logical representation as booleans. trueValues and falseValues are arrays which can be customised to user need. The default values for these are in the additional properties section below. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#boolean).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['true'], ['false']]
rows = extract(data, schema=Schema(fields=[fields.BooleanField(name='name')]))
print(rows)
```

## Reference

```yaml reference
references:
  - frictionless.fields.BooleanField
```
