---
script:
  basepath: data
topics:
  collapseDepth: 3
---

# Dialect Class

The Table Dialect is a core Frictionless Data concept meaning a metadata information regarding tabular data source. The Table Dialect concept give us an ability to manage table header and any details related to specific formats.

## Dialect

The Dialect class instance are accepted by many classes and functions:

- Resource
- describe
- extract
- validate
- and more

You just need to create a Dialect instance using desired options and pass to the classed and function from above. We will show it on this examplar table:

```bash script tabs=CLI
cat capital-3.csv
```

## Header

It's a boolean flag which defaults to `True` indicating whether the data has a header row or not. In the following example the header row will be treated as a data row:

```python script tabs=Python
from frictionless import Resource, Dialect

dialect = Dialect(header=False)
with Resource('capital-3.csv', dialect=dialect) as resource:
      print(resource.header.labels)
      print(resource.to_view())
```

## Header Rows

If header is `True` which is default, this parameters indicates where to find the header row or header rows for a multiline header. Let's see on example how the first two data rows can be treated as a part of a header:

```python script tabs=Python
from frictionless import Resource, Dialect

dialect = Dialect(header_rows=[1, 2, 3])
with Resource('capital-3.csv', dialect=dialect) as resource:
    print(resource.header)
    print(resource.to_view())
```

## Header Join

If there are multiple header rows which is managed by `header_rows` parameter, we can set a string to be a separator for a header's cell join operation. Usually it's very handy for some "fancy" Excel files. For the sake of simplicity, we will show on a CSV file:

```python script tabs=Python
from frictionless import Resource, Dialect

dialect = Dialect(header_rows=[1, 2, 3], header_join='/')
with Resource('capital-3.csv', dialect=dialect) as resource:
    print(resource.header)
    print(resource.to_view())
```

## Header Case

By default a header is validated in a case sensitive mode. To disable this behaviour we can set the `header_case` parameter to `False`. This option is accepted by any Dialect and a dialect can be passed to `extract`, `validate` and other functions. Please note that it doesn't affect a resulting header it only affects how it's validated:

```python script tabs=Python
from frictionless import Resource, Schema, Dialect, fields

dialect = Dialect(header_case=False)
schema = Schema(fields=[fields.StringField(name="ID"), fields.StringField(name="NAME")])
with Resource('capital-3.csv', dialect=dialect, schema=schema) as resource:
  print(f'Header: {resource.header}')
  print(f'Valid: {resource.header.valid}')  # without "header_case" it will have 2 errors
```

## Comment Char

Specifies char used to comment the rows:

```python script tabs=Python
from frictionless import Resource, Dialect

dialect = Dialect(comment_char="#")
with Resource(b'name\n#row1\nrow2', format="csv", dialect=dialect) as resource:
    print(resource.read_rows())
```

## Comment Rows

A list of rows to ignore:

```python script tabs=Python
from frictionless import Resource, Dialect

dialect = Dialect(comment_rows=[2])
with Resource(b'name\nrow1\nrow2', format="csv", dialect=dialect) as resource:
    print(resource.read_rows())
```

## Skip Blank Rows

Ignores rows if they are completely blank.

```python script tabs=Python
from frictionless import Resource, Dialect

dialect = Dialect(skip_blank_rows=True)
with Resource(b'name\n\nrow2', format="csv", dialect=dialect) as resource:
    print(resource.read_rows())
```

## Reference

```yaml reference
references:
  - frictionless.Dialect
  - frictionless.Control
```
