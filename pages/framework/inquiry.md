# Inquiry Class

The Inquiry gives you an ability to create arbitrary validation jobs containing a set of individual validation tasks.

## Creating Inquiry

Let's create an inquiry that includes an individual file validation and a resource validation:

```python title="Python"
from frictionless import Inquiry

inquiry = Inquiry({'tasks': [
  {'source': 'data/capital-valid.csv'},
  {'source': 'data/capital-invalid.csv'},
]})
inquiry.to_yaml('capital.inquiry.yaml')
```

## Validating Inquiry

Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions have. As usual, let' run validation:

```bash title="CLI"
frictionless validate capital.inquiry.yaml
```
```
# -----
# valid: data/capital-valid.csv
# -----
# -------
# invalid: data/capital-invalid.csv
# -------

===  =====  ===============  ================================================================================================
row  field  code             message
===  =====  ===============  ================================================================================================
         3  duplicate-label  Label "name" in the header at position "3" is duplicated to a label: at position "2"
 10      3  missing-cell     Row at position "10" has a missing cell in field "name2" at position "3"
 11         blank-row        Row at position "11" is completely blank
 12      1  type-error       Type error in the cell "x" in row "12" and field "id" at position "1": type is "integer/default"
 12      4  extra-cell       Row at position "12" has an extra value in field at position "4"
===  =====  ===============  ================================================================================================
```

At first sight, it's no clear why such a construct exists but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power. Last but not least, the Inquiry will use multiprocessing if there are more than 1 task provided.
