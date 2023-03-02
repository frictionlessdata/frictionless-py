---
script:
  basepath: data
---

# Catalog Class

```markdown remark type=danger
This feature is currently experimental. The API might change without notice
```

Catalog is a set of data packages.

## Creating Catalog

We can create a catalog providing a list of data packages:

```python tabs=Python
from frictionless import Catalog, Dataset, Package

catalog = Catalog(datasets=[Dataset(name='name', package=Package('tables/*'))])
```

## Describing Catalog

Usually Catalog is used to describe some external set of datasets like a CKAN instance or a Github user or search. For example:

```python tabs=Python
from frictionless import Catalog

catalog = Catalog('https://demo.ckan.org/dataset/')
print(catalog)
```

## Dataset Management

The core purpose of having a catalog is to provide an ability to have a set of datasets. The Catalog class provides useful methods to manage datasets:

```python tabs=Python
from frictionless import Catalog

catalog = Catalog('https://demo.ckan.org/dataset/')
catalog.dataset_names
catalog.has_dataset
catalog.add_dataset
catalog.get_dataset
catalog.clear_datasets
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
  - frictionless.Dataset
```
