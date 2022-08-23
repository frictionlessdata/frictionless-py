# Gsheets Format

Frictionless supports parsing Google Sheets data as a file format.

```bash tabs=CLI
pip install frictionless[gsheets]
pip install 'frictionless[gsheets]' # for zsh shell
```

## Reading Data

You can read from Google Sheets using `Package/Resource`, for example:

```python tabs=Python
from pprint import pprint
from frictionless import Resource

path='https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing'
resource = Resource(path=path)
pprint(resource.read_rows())
```
```
[{'id': 1, 'name': 'english'}, {'id': 2, 'name': '中国人'}]
```

## Writing Data

The same is actual for writing:

```python tabs=Python
from frictionless import Resource, formats

control = formats.GsheetsControl(credentials=".google.json")
resource = Resource(path='data/table.csv')
resource.write("https://docs.google.com/spreadsheets/d/<id>/edit", control=control})
```

## Configuration

There is a dialect to configure how Frictionless read and write files in this format. For example:

```python tabs=Python
from frictionless import Resource, formats

control = formats.GsheetsControl(credentials=".google.json")
resource = Resource(path='data/table.csv')
resource.write("https://docs.google.com/spreadsheets/d/<id>/edit", control=control)
```

## Reference

```yaml reference
references:
  - frictionless.formats.GsheetsControl
```
