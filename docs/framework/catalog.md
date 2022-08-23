---
script:
  basepath: data
---

# Catalog Class

Catalog is a set of data packages.

## Creating Catalog

We can create a catalog providing a list of data packages:

```python tabs=Python
from frictionless import Catalog, Package

catalog = Catalog(packages=[Package('tables/*')])
```

## Describing Catalog

Usually Catalog is used to describe some external set of datasets like a CKAN instance or a Github user or search. For example:

```python tabs=Python
from frictionless import Catalog

catalog = Catalog('https://demo.ckan.org/dataset/')
print(catalog)
```

## Package Management

The core purpose of having a catalog is to provide an ability to have a set of packages. The Catalog class provides useful methods to manage packages:

```python tabs=Python
from frictionless import Catalog

catalog = Catalog('https://demo.ckan.org/dataset/')
catalog.package_names
catalog.has_package
catalog.add_package
catalog.get_package
catalog.clear_packages
```

## Saving Descriptor

As any of the Metadata classes the Catalog class can be saved as JSON or YAML:

```python tabs=Python
from frictionless import Package

catalog = Catalog('https://demo.ckan.org/dataset/')
catalog.to_json('datacatalog.json') # Save as JSON
catalog.to_yaml('datacatalog.yaml') # Save as YAML
```

## Reference

```yaml reference
references:
  - frictionless.Catalog
```
