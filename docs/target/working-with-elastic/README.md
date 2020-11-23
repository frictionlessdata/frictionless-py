# Working with ElasticSearch

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1EcC5p8-ctE4d0ViA0_lswJTE5-06mHTu)



> Status: **PLUGIN / EXPERIMENTAL**

Frictionless supports reading and writing ElasticSearch datasets.


```bash
! pip install frictionless[elastic]
```

## Reading from ElasticSearch

You can read a ElasticSearch dataset:

```python
from frictionless import Package

package = Package.from_elasticsearch(es='<es_instance>')
print(package)
for resource in package.resources:
  print(resource.read_rows())
```

## Wriring to ElasticSearch

You can write a dataset to ElasticSearch:

```python
from frictionless import Package

package = Package('path/to/datapackage.json')
package.to_ckan(es='<es_instance>')
```

## Configuring ElasticSearch

> ElasticSearch dialect is not yet available