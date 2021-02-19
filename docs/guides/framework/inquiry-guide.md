---
title: Inquiry Guide
---

The Inquiry gives you an ability to create arbitrary validation jobs containing a set of individual validation tasks.

## Creating Inquiry

Let's create an inquiry that includes an individual file validation and a resource validation:

```python title="Python"
from frictionless import Inquiry

inquiry = Inquiry({'tasks': [
  {'source': 'data/capital-valid.csv'},
  {'source': 'tmp/capital.resource.json', 'basepath': '.'},
]})
inquiry.to_yaml('tmp/capital.inquiry.yaml')
```

## Validating Inquiry

Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions have. As usual, let' run validation:

```bash title="CLI"
frictionless validate tmp/capital.inquiry.yaml
```
```
---
valid: data/capital-valid.csv
---
---
invalid: ./data/capital-invalid.csv
---

====  =====  ================  ====================================================================================================================
row   field  code              message
====  =====  ================  ====================================================================================================================
None      3  duplicate-header  Header "name" in field at position "3" is duplicated to header in another field: at position "2"
  10      3  missing-cell      Row at position "10" has a missing cell in field "name2" at position "3"
  11  None   blank-row         Row at position "11" is completely blank
  12      4  extra-cell        Row at position "12" has an extra value in field at position "4"
  12      1  type-error        The cell "x" in row at position "12" and field "id" at position "1" has incompatible type: type is "integer/default"
====  =====  ================  ====================================================================================================================
```

At first sight, it's no clear why such a construct exists but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power. Last but not least, the Inquiry will use multiprocessing if there are more than 1 task provided.
