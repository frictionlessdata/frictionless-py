# Working with CKAN

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1NrInE94OamiLGmlAlGQ6kmwwGmnA5iav)



>Status: **PLUGIN / EXPERIMENTAL**

Frictionless supports reading and writing CKAN datasets.

## Reading from CKAN

You can read a CKAN dataset:

```python
from frictionless import Package

package = Package.from_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Wriring to CKAN

You can write a dataset to CKAN:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan(base_url='<base_url>', dataset_id='<dataset_id>', api_key='<api_key>')
```

## Configuring CKAN

> CKAN dialect is not yet available