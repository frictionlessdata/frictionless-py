# Working with Pandas

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1b6d-oMN0Mi2vMlTN8KwY11ezAgRd-dhl)



> Status: **PLUGIN / STABLE**

Frictionless supports reading and writing Pandas dataframes.


```bash
! pip install frictionless[pandas]
```

## Reading from Pandas

You can read a Pandas dataframe:

```python
from frictionless import Package

package = Package.from_pandas(dataframes=['table1': '<df1>', 'tables2': '<df2>'])
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Wriring to Pandas

You can write a dataset to Pandas:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
dataframes = package.to_pandas()
```

## Configuring Pandas

> Not supported yet