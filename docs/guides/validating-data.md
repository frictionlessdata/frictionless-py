---
script:
  basepath: data
---

# Validating Data

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Tabular data validation is a process of identifying problems that have occured in your data so you can correct them. Let's explore how Frictionless helps to achieve this task using an invalid data table example:

> Download [`capital-invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/capital-invalid.csv) to reproduce the examples (right-click and "Save link as")..

```bash script tabs=CLI
cat capital-invalid.csv
```

```python script tabs=Python
with open('capital-invalid.csv') as file:
    print(file.read())
```

We can validate this file by using both command-line interface and high-level functions. Frictionless provides comprehensive error details so that errors can be understood by the user. Continue reading to learn the validation process in detail.

```bash script tabs=CLI
frictionless validate capital-invalid.csv
```

```python script tabs=Python
from pprint import pprint
from frictionless import validate

report = validate('capital-invalid.csv')
print(report)
```

## Validate Functions

The high-level interface for validating data provided by Frictionless is a set of `validate` functions:
- `validate`: detects the source type and validates data accordingly
- `Schema.validate_descriptor`: validates a schema's metadata
- `resource.validate`: validates a resource's data and metadata
- `package.validate`: validates a package's data and metadata
- `inquiry.validate`: validates a special `Inquiry` object which represents a validation task instruction

On the command-line, there is only one command but there is a flag to adjust the behavior. It's useful when you have a file which has a ambiguous type, for example, a json file containing a data instead of metadata:

```bash tabs=CLI
frictionless validate your-data.csv
frictionless validate your-schema.yaml --type schema
frictionless validate your-data.csv --type resource
frictionless validate your-package.json --type package
frictionless validate your-inquiry.yaml --type inquiry
```

As a reminder, in the Frictionless ecosystem, a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema. This concept is described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction).

## Validating a Schema

The `Schema.validate_descriptor` function is the only function validating solely metadata. To see this work, let's create an invalid table schema:

```python script tabs=Python
import yaml
from frictionless import Schema

descriptor = {}
descriptor['fields'] = 'bad' # must be a list
with open('bad.schema.yaml', 'w') as file:
    yaml.dump(descriptor, file)
```

And let's validate this schema:

```bash script tabs=CLI
frictionless validate bad.schema.yaml
```

```python script tabs=Python
from pprint import pprint
from frictionless import validate

report = validate('bad.schema.yaml')
pprint(report)
```

We see that the schema is invalid and the error is displayed. Schema validation can be very useful when you work with different classes of tables and create schemas for them. Using this function will ensure that the metadata is valid.

## Validating a Resource

As was shown in the ["Describing Data" guide](https://framework.frictionlessdata.io/docs/guides/describing-data), a resource is a container having both metadata and data. We need to create a resource descriptor and then we can validate it:

```bash script tabs=CLI
frictionless describe capital-invalid.csv > capital.resource.yaml
```

```python script tabs=Python
from frictionless import describe

resource = describe('capital-invalid.csv')
resource.to_yaml('capital.resource.yaml')
```

Note: this example uses YAML for the resource descriptor format, but Frictionless also supports JSON format also.

Let's now validate to ensure that we are getting the same result that we got without using a resource:

```bash script tabs=CLI
frictionless validate capital.resource.yaml
```

```python script tabs=Python output=python
from frictionless import validate

report = validate('capital.resource.yaml')
print(report)
```

Okay, why do we need to use a resource descriptor if the result is the same? The reason is metadata + data packaging. Let's extend our resource descriptor to show how you can edit and validate metadata:

```python script tabs=Python
from frictionless import describe

resource = describe('capital-invalid.csv')
resource.add_defined('stats')  # TODO: fix and remove this line
resource.stats.md5 = 'ae23c74693ca2d3f0e38b9ba3570775b' # this is a made up incorrect
resource.stats.bytes = 100 # this is wrong
resource.to_yaml('capital.resource-bad.yaml')
```

We have added a few incorrect, made up attributes to our resource descriptor as an example. Now, the validation below reports these errors in addition to all the errors we had before. This example shows how concepts like Data Resource can be extremely useful when working with data.

```bash script tabs=CLI
frictionless validate capital.resource-bad.yaml  # TODO: it should have 7 errors
```

```python script tabs=Python
from frictionless import validate

report = validate('capital.resource-bad.yaml')
print(report)
```

## Validating a Package

A package is a set of resources + additional metadata. To showcase a package validation we need to use one more tabular file:

> Download [`capital-valid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/capital-valid.csv) to reproduce the examples (right-click and "Save link as").


```bash script tabs=CLI
cat capital-valid.csv
```

```python script tabs=Python
with open('capital-valid.csv') as file:
    print(file.read())
```

Now let's describe and validate a package which contains the data files we have seen so far:

```bash script tabs=CLI
frictionless describe capital-*id.csv > capital.package.yaml
frictionless validate capital.package.yaml
```

```python script tabs=Python
from frictionless import describe, validate

# create package descriptor
package = describe("capital-*id.csv")
package.to_yaml("capital.package.yaml")
# validate
report = validate("capital.package.yaml")
print(report)
```

As we can see, the result is in a similar format to what we have already seen, and shows errors as we expected: we have one invalid resource and one valid resource.

## Validating an Inquiry

> The Inquiry is an advanced concept mostly used by software integrators. For example, under the hood, Frictionless Framework uses inquiries to implement client-server validation within the built-in API. Please skip this section if this information feels unnecessary for you.

Inquiry is a declarative representation of a validation job. It gives you an ability to create, export, and share arbitrary validation jobs containing a set of individual validation tasks. Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions.

Let's create an Inquiry that includes an individual file validation and a resource validation. In this example we will use the data file, `capital-valid.csv` and the resource, `capital.resource.json` which describes the invalid data file we have already seen:

```python script tabs=Python
from frictionless import Inquiry, InquiryTask

inquiry = Inquiry(tasks=[
    InquiryTask(path='capital-valid.csv'),
    InquiryTask(resource='capital.resource.yaml'),
])
inquiry.to_yaml('capital.inquiry.yaml')
```
As usual, let's run validation:

```bash script tabs=CLI
frictionless validate capital.inquiry.yaml
```

```python script tabs=Python
from frictionless import validate

report = validate("capital.inquiry.yaml")
print(report)
```

At first sight, it might not be clear why such a construct exists, but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power.

> The Inquiry will use multiprocessing if there is the `parallel` flag provided. It might speed up your validation dramatically especially on a 4+ cores processor.

## Validation Report

All the `validate` functions return a Validation Report. This is a unified object containing information about a validation: source details, the error, etc. Let's explore a report:

```python script tabs=Python output=python
from frictionless import validate

report = validate('capital-invalid.csv', pick_errors=['duplicate-label'])
print(report)
```

As we can see, there is a lot of information; you can find a detailed description of the Validation Report in the [API Reference](../docs/framework/report.html#reference). Errors are grouped by tasks (i.e. data files); for some validation there can be dozens of tasks. Let's use the `report.flatten` function to simplify the representation of errors. This function helps to represent a report as a list of errors:

```python script tabs=Python output=python
from pprint import pprint
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
pprint(report.flatten(["rowNumber", "fieldNumber", "code", "message"]))
```

In some situations, an error can't be associated with a task; then it goes to the top-level `report.errors` property:

```python script tabs=Python output=python
from frictionless import validate

report = validate("bad.json", type='schema')
print(report)
```

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tasks[].errors`, properties that can contain the Error object. Let's explore it by taking a deeper look at the `duplicate-label` error:

```python script tabs=Python
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
error = report.error  # this is only available for one table / one error sitution
print(f'Type: "{error.type}"')
print(f'Title: "{error.title}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```

Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-label` error:

```python script tabs=Python output=python
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
error = report.error  # this is only available for one table / one error sitution
print(error)
```
```
{'code': 'duplicate-label',
 'description': 'Two columns in the header row have the same value. Column '
                'names should be unique.',
 'fieldName': 'name2',
 'fieldNumber': 3,
 'fieldPosition': 3,
 'label': 'name',
 'labels': ['id', 'name', 'name'],
 'message': 'Label "name" in the header at position "3" is duplicated to a '
            'label: at position "2"',
 'name': 'Duplicate Label',
 'note': 'at position "2"',
 'rowPositions': [1],
 'tags': ['#table', '#header', '#label']}
```

Please explore the [Errors Reference](/docs/references/errors-reference) to learn about all the available errors and their properties.

## Available Checks

There are various validation checks included in the core Frictionless Framework along with an ability to create custom checks. See [Validation Checks](../checks/cell.html) for a list of available checks.

```python script tabs=Python
from pprint import pprint
from frictionless import validate, checks

checks = [checks.sequential_value(field_name='id')]
report = validate('capital-invalid.csv', checks=checks)
pprint(report.flatten(["rowNumber", "fieldNumber", "type", "note"]))
```
```
[[None, 3, 'duplicate-label', 'at position "2"'],
 [10, 3, 'missing-cell', ''],
 [10, 1, 'sequential-value', 'the value is not sequential'],
 [11, None, 'blank-row', ''],
 [12, 1, 'type-error', 'type is "integer/default"'],
 [12, 4, 'extra-cell', '']]
```
> Note that only the Baseline Check is enabled by default. Other built-in checks need to be activated as shown below.

## Custom Checks

There are many cases when built-in Frictionless checks are not enough. For instance, you might want to create a business logic rule or specific quality requirement for the data. With Frictionless it's very easy to use your own custom checks. Let's see with an example:

```python script tabs=Python
from pprint import pprint
from frictionless import Check, validate, errors

# Create check
class forbidden_two(Check):
    Errors = [errors.CellError]
    def validate_row(self, row):
        if row['header'] == 2:
            note = '2 is forbidden!'
            yield errors.CellError.from_row(row, note=note, field_name='header')

# Validate table
source = b'header\n1\n2\n3'
report = validate(source,  format='csv', checks=[forbidden_two()])
pprint(report.flatten(["rowNumber", "fieldNumber", "code", "note"]))
```

Usually, it also makes sense to create a custom error for your custom check. The Check class provides other useful methods like `validate_header` etc. Please read the [API Reference](../references/api-reference.md) for more details.

Learn more about custom checks in the [Check Guide](.../docs/checks/baseline.html#reference).

## Pick/Skip Errors

We can pick or skip errors by providing a list of error codes. This is useful when you already know your data has some errors, but you want to ignore them for now. For instance, if you have a data table with repeating header names. Let's see an example of how to pick and skip errors:

```python script tabs=Python
from pprint import pprint
from frictionless import validate

report1 = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
report2 = validate("capital-invalid.csv", skip_errors=["duplicate-label"])
pprint(report1.flatten(["rowNumber", "fieldNumber", "type"]))
pprint(report2.flatten(["rowNumber", "fieldNumber", "type"]))
```

It's also possible to use error tags (for more information please consult the [Errors Reference](../references/errors-reference.md)):

```python script tabs=Python
from pprint import pprint
from frictionless import validate

report1 = validate("capital-invalid.csv", pick_errors=["#header"])
report2 = validate("capital-invalid.csv", skip_errors=["#row"])
pprint(report1.flatten(["rowNumber", "fieldNumber", "type"]))
pprint(report2.flatten(["rowNumber", "fieldNumber", "type"]))
```

## Limit Errors

This option allows you to limit the amount of errors, and can be used when you need to do a quick check or want to "fail fast". For instance, here we use `limit_errors` to find just the 1st error and add it to our report:

```python title="Python"
from pprint import pprint
from frictionless import validate

report = validate("capital-invalid.csv", limit_errors=1)
pprint(report.flatten(["rowNumber", "fieldNumber", "type"]))
```
```
[[None, 3, 'duplicate-label']]
```
