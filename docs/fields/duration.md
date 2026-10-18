# Duration Field

## Overview

A duration of time. We follow the definition of XML Schema duration datatype directly
and that definition is implicitly inlined here. Read more in [Table Schema Standard](https://specs.frictionlessdata.io/table-schema/#duration).

## Constraints

Duration fields support `minimum`, `maximum`, `exclusiveMinimum`, and
`exclusiveMaximum` with ISO 8601 duration values. Duration bounds require
Data Package v2.

Comparisons follow the [XML Schema duration order](https://www.w3.org/TR/xmlschema-2/#duration-order).
Calendar months and years are not converted to a fixed number of days. Some
durations, such as `P1M` and `P30D`, have no determinate order; these comparisons
fail the bound constraint, including inclusive bounds. Missing values remain
valid unless the field is required.

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
