---
script:
  basepath: data
---

# Field Steps

The Field steps are responsible for managing a Table Schema's fields. You can add or remove them along with more complex operations like unpacking.

## Add Field

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_add(name="note", value="eu", descriptor={"type": "string"}),
    ]
)
print(target.schema)
print(target.to_view())
```

## Filter Fields

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_filter(names=["id", "name"]),
    ]
)
print(target.schema)
print(target.to_view())
```

## Merge Fields

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
     source,
     steps=[
     	 # seperator argument can be used to set delimeter. Default value is '-'
    	 # preserve argument keeps the original fields
         steps.field_merge(name="details", from_names=["name", "population"], preserve=True)
     ],
)
print(target.schema)
print(target.to_view())
```

## Move Field

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_move(name="id", position=3),
    ]
)
print(target.schema)
print(target.to_view())
```

## Pack Fields

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
    	# field_type returns packed fields as JSON Object. Default value for field_type is 'array'
    	# preserve argument keeps the original fields
        steps.field_pack(name="details", from_names=["name", "population"], as_object=True, preserve=True)
    ]
)
print(target.schema)
print(target.to_view())
```

## Remove Field

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_remove(names=["id"]),
    ]
)
print(target.schema)
print(target.to_view())
```

## Split Field

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_split(name="name", to_names=["name1", "name2"], pattern="a"),
    ]
)
print(target.schema)
print(target.to_view())
```

## Unpack Field

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", value=[1, 1], descriptor={"type": "string"}),
        steps.field_unpack(name="id", to_names=["id2", "id3"]),
    ]
)
print(target.schema)
print(target.to_view())
```

## Update Field

```python script tabs=Python
from pprint import pprint
from frictionless import Package, Resource, transform, steps

source = Resource(path="transform.csv")
target = transform(
    source,
    steps=[
        steps.field_update(name="id", value=str, descriptor={"type": "string"}),
    ]
)
print(target.schema)
print(target.to_view())
```
