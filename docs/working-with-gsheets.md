# Working with Google Sheets

> Status: **EXPERIMENTAL**

Frictionless supports parsing Google Sheets data as a file format.

```sh
!pip install frictionless[gsheets]
```

## Reading from Google Sheets

You can read from Google Sheets using `Package/Resource` or `Table` API, for example:

```python
from frictionless import Resource

resource = Resource(path='https://docs.google.com/spreadsheets/d/1mHIWnDvW9cALRMq9OdNfRwjAthCUFUOACPp0Lkyl7b4/edit?usp=sharing')
print(resource.read_rows())
```

## Writing to Google Sheets

> Not supported

## Configuring Google Sheets

> Not supported


