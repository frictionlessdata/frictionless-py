---
script:
  basepath: data
---

# Resource Steps

The Resource steps are only available for a package transformation. This includes some basic resource management operations like adding or removing resources along with the hierarchical `transform_resource` step.

## Add Resource

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

## Remove Resource

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

## Transform Resource

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

## Update Resource

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