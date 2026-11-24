---
script:
  basepath: data
---

# Inquiry Class

The Inquiry gives you an ability to create arbitrary validation jobs containing a set of individual validation tasks.

## Creating Inquiry

Let's create an inquiry that includes an individual file validation and a resource validation:

```python script tabs=Python
from frictionless import Inquiry

inquiry = Inquiry.from_descriptor({'tasks': [
  {'path': 'capital-valid.csv'},
  {'path': 'capital-invalid.csv'},
]})
inquiry.to_yaml('capital.inquiry-example.yaml')
print(inquiry)
```

## Validating Inquiry

Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions have. As usual, let' run validation:

```bash script tabs=CLI
frictionless validate capital.inquiry-example.yaml
```

At first sight, it's not clear why such a construct exists but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power. Inquiry validation can use multiprocessing if the `parallel` flag is provided.

## Reference

```yaml reference
references:
  - frictionless.Inquiry
  - frictionless.InquiryTask
```
