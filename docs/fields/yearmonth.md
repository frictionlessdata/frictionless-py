# Yearmonth Field

## Overview

A specific month in a specific year as per XMLSchema gYearMonth. Usual lexical representation is: YYYY-MM. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#yearmonth).

## Example

```python script tabs=Python
from frictionless import Schema, extract, fields

data = [['name'], ['2022-08']]
rows = extract(data, schema=Schema(fields=[fields.YearmonthField(name='name')]))
print(rows)
```

## Reference

```markdown tabs=Select
Select reference to show
```

```yaml reference tabs=YearmonthField
name: frictionless.fields.YearmonthField
```
