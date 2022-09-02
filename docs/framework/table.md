---
script:
  basepath: data
---

# Table Classes

## Table Header

After opening a resource you get access to a `resource.header` object which describes the resource in more detail. This is a list of normalized labels but also provides some additional functionality. Let's take a look:

```python script tabs=Python
from frictionless import Resource

with Resource('capital-3.csv') as resource:
  print(f'Header: {resource.header}')
  print(f'Labels: {resource.header.labels}')
  print(f'Fields: {resource.header.fields}')
  print(f'Field Names: {resource.header.field_names}')
  print(f'Field Numbers: {resource.header.field_numbers}')
  print(f'Errors: {resource.header.errors}')
  print(f'Valid: {resource.header.valid}')
  print(f'As List: {resource.header.to_list()}')
```

The example above shows a case when a header is valid. For a header that contains errors in its tabular structure, this information can be very useful, revealing discrepancies, duplicates or missing cell information:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

with Resource([['name', 'name'], ['value', 'value']]) as resource:
    pprint(resource.header.errors)
```

## Table Row

The `extract`, `resource.read_rows()` and other functions return or yield row objects. In Python, this returns a dictionary with the following information. Note: this example uses the [Detector object](/docs/guides/framework/detector-guide), which tweaks how different aspects of metadata are detected.

```python script tabs=Python
from frictionless import Resource, Detector

detector = Detector(schema_patch={'missingValues': ['1']})
with Resource('capital-3.csv', detector=detector) as resource:
  for row in resource.row_stream:
    print(f'Row: {row}')
    print(f'Cells: {row.cells}')
    print(f'Fields: {row.fields}')
    print(f'Field Names: {row.field_names}')
    print(f'Value of field "name": {row["name"]}') # accessed as a dict
    print(f'Row Number: {row.row_number}') # counted row number starting from 1
    print(f'Blank Cells: {row.blank_cells}')
    print(f'Error Cells: {row.error_cells}')
    print(f'Errors: {row.errors}')
    print(f'Valid: {row.valid}')
    print(f'As Dict: {row.to_dict(json=False)}')
    print(f'As List: {row.to_list(json=True)}') # JSON compatible data types
    break
```

As we can see, this output provides a lot of information which is especially useful when a row is not valid. Our row is valid but we demonstrated how it can preserve data about missing values. It also preserves data about all cells that contain errors:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

with Resource([['name'], ['value', 'value']]) as resource:
    for row in resource.row_stream:
        pprint(row.errors)
```

## Reference

```yaml reference
references:
  - frictionless.Header
  - frictionless.Row
```
