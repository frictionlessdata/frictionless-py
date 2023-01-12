---
script:
  basepath: data
---

# Resource Steps

The Resource steps are only available for a package transformation (except for `steps.resource_update` available for standalone resources). This includes some basic resource management operations like adding or removing resources along with the hierarchical `transform_resource` step.

## Add Resource

This step add a new resource to a data package.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_add(name='extra', descriptor={'path': 'transform.csv'}),
    ],
)
print(target.resource_names)
print(target.get_resource('extra').schema)
print(target.get_resource('extra').to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.resource_add
```

## Remove Resource

This step remove an existent resource from a data package.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_remove(name='main'),
    ],
)
print(target)
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.resource_remove
```

## Transform Resource

It's a hierarchical step allowing to transform a data package's resource. It's possible to use any resource steps as a part of this package step.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_transform(name='main', steps=[
            steps.row_sort(field_names=['name'])
        ]),
    ],
)
print(target.resource_names)
print(target.get_resource('main').schema)
print(target.get_resource('main').to_view())
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.resource_transform
```

## Update Resource

This step update a resource's metadata. It can be used for both resource and package transformations.

### Example

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Package(resources=[Resource(name='main', path="transform.csv")])
target = transform(
    source,
    steps=[
        steps.resource_update(
          name='main',
          descriptor={'title': 'Main Resource', 'description': 'For the docs'}
        ),
    ],
)
print(target.get_resource('main'))
```

### Reference

```yaml reference
level: 4
references:
  - frictionless.steps.resource_update
```
