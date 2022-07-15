---
title: Validation Guide
prepare:
  - cp data/capital-invalid.csv capital-invalid.csv
  - cp data/capital-valid.csv capital-valid.csv
cleanup:
  - rm capital-invalid.csv
  - rm capital-valid.csv
  - rm capital.schema.yaml
  - rm capital.resource.yaml
  - rm capital.package.yaml
  - rm capital.inquiry.yaml
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Tabular data validation is a process of identifying problems that have occured in your data so you can correct them. Let's explore how Frictionless helps to achieve this task using an invalid data table example:

> Download [`capital-invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-invalid.csv) to reproduce the examples (right-click and "Save link as")..

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat capital-invalid.csv
```
```csv title="Data: capital-invalid.csv"
id,name,name
1,London,Britain
2,Berlin,Germany
3,Paris,France
4,Madrid,Spain
5,Rome,Italy
6,Zagreb,Croatia
7,Athens,Greece
8,Vienna,Austria
8,Warsaw

x,Tokio,Japan,review
```

</TabItem>
<TabItem value="python">

```python script
with open('capital-invalid.csv') as file:
    print(file.read())
```
```csv title="Data: capital-invalid.csv"
id,name,name
1,London,Britain
2,Berlin,Germany
3,Paris,France
4,Madrid,Spain
5,Rome,Italy
6,Zagreb,Croatia
7,Athens,Greece
8,Vienna,Austria
8,Warsaw

x,Tokio,Japan,review
```

</TabItem>
</Tabs>

We can validate this file by using both command-line interface and high-level functions. Frictionless provides comprehensive error details so that errors can be understood by the user. Continue reading to learn the validation process in detail.

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless validate capital-invalid.csv
```
```text title="Validation Report: capital-valid.csv"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-----------------------------------+-------------------------+
| Description                       | Size/Name/Count         |
+===================================+=========================+
| File name                         | capital-invalid.csv |
+-----------------------------------+-------------------------+
| File size (bytes)                 | 171                     |
+-----------------------------------+-------------------------+
| Total Time Taken (sec)            | 0.007                   |
+-----------------------------------+-------------------------+
| Total Errors                      | 5                       |
+-----------------------------------+-------------------------+
| Duplicate Label (duplicate-label) | 1                       |
+-----------------------------------+-------------------------+
| Missing Cell (missing-cell)       | 1                       |
+-----------------------------------+-------------------------+
| Blank Row (blank-row)             | 1                       |
+-----------------------------------+-------------------------+
| Type Error (type-error)           | 1                       |
+-----------------------------------+-------------------------+
| Extra Cell (extra-cell)           | 1                       |
+-----------------------------------+-------------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import validate

report = validate('capital-invalid.csv')
print(report.to_summary())
```
```text title="Validation Report: capital-valid.csv"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-----------------------------------+-------------------------+
| Description                       | Size/Name/Count         |
+===================================+=========================+
| File name                         | capital-invalid.csv |
+-----------------------------------+-------------------------+
| File size (bytes)                 | 171                     |
+-----------------------------------+-------------------------+
| Total Time Taken (sec)            | 0.007                   |
+-----------------------------------+-------------------------+
| Total Errors                      | 5                       |
+-----------------------------------+-------------------------+
| Duplicate Label (duplicate-label) | 1                       |
+-----------------------------------+-------------------------+
| Missing Cell (missing-cell)       | 1                       |
+-----------------------------------+-------------------------+
| Blank Row (blank-row)             | 1                       |
+-----------------------------------+-------------------------+
| Type Error (type-error)           | 1                       |
+-----------------------------------+-------------------------+
| Extra Cell (extra-cell)           | 1                       |
+-----------------------------------+-------------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
</Tabs>

## Validate Functions

The high-level interface for validating data provided by Frictionless is a set of `validate` functions:
- `validate`: detects the source type and validates data accordingly
- `validate_schema`: validates a schema's metadata
- `validate_resource`: validates a resource's data and metadata
- `validate_package`: validates a package's data and metadata
- `validate_inquiry`: validates a special `Inquiry` object which represents a validation task instruction

On the command-line, there is only one command but there is a flag to adjust the behavior. It's useful when you have a file which has a ambiguous type, for example, a json file containing a data instead of metadata:

```bash title="CLI"
frictionless validate your-data.csv
frictionless validate your-schema.yaml --type schema
frictionless validate your-data.csv --type resource
frictionless validate your-package.json --type package
frictionless validate your-inquiry.yaml --type inquiry
```

As a reminder, in the Frictionless ecosystem, a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema. This concept is described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction).

## Validating a Schema

The `validate_schema` function is the only function validating solely metadata. To see this work, let's create an invalid table schema:

```python script title="Python"
from frictionless import Schema

schema = Schema()
schema.fields = {} # must be a list
schema.to_yaml('capital.schema.yaml')
```

And let's validate this schema:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless validate capital.schema.yaml
```
```text title="Validation Report: capital.schema.yaml"
# -------
# invalid: capital.schema.yaml
# -------
code          message
------------  -------------------------------------------------------------------------------------------------------------------
schema-error  Schema is not valid: "{} is not of type 'array'" at "fields" in metadata and at "properties/fields/type" in profile
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import validate
from tabulate import tabulate

report = validate('capital.schema.yaml')
errors = report.flatten(['code','message'])
print(tabulate(errors, headers = ['code', 'message']))
```
```text title="Validation Report: capital.schema.yaml"
# -------
# invalid: capital.schema.yaml
# -------
code          message
------------  -------------------------------------------------------------------------------------------------------------------
schema-error  Schema is not valid: "{} is not of type 'array'" at "fields" in metadata and at "properties/fields/type" in profile
```

</TabItem>
</Tabs>

We see that the schema is invalid and the error is displayed. Schema validation can be very useful when you work with different classes of tables and create schemas for them. Using this function will ensure that the metadata is valid.

## Validating a Resource

As was shown in the ["Describing Data" guide](https://framework.frictionlessdata.io/docs/guides/describing-data), a resource is a container having both metadata and data. We need to create a resource descriptor and then we can validate it:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless describe capital-invalid.csv > capital.resource.yaml
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import describe

resource = describe('capital-invalid.csv')
resource.to_yaml('capital.resource.yaml')
```

</TabItem>
</Tabs>

Note: this example uses YAML for the resource descriptor format, but Frictionless also supports JSON format also.

Let's now validate to ensure that we are getting the same result that we got without using a resource:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless validate capital.resource.yaml
```
```text title="Validation Report: capital.resource.yaml"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-----------------------------------+---------------------+
| Description                       | Size/Name/Count     |
+===================================+=====================+
| File name                         | capital-invalid.csv |
+-----------------------------------+---------------------+
| File size (bytes)                 | 171                 |
+-----------------------------------+---------------------+
| Total Time Taken (sec)            | 0.007               |
+-----------------------------------+---------------------+
| Total Errors                      | 5                   |
+-----------------------------------+---------------------+
| Duplicate Label (duplicate-label) | 1                   |
+-----------------------------------+---------------------+
| Missing Cell (missing-cell)       | 1                   |
+-----------------------------------+---------------------+
| Blank Row (blank-row)             | 1                   |
+-----------------------------------+---------------------+
| Type Error (type-error)           | 1                   |
+-----------------------------------+---------------------+
| Extra Cell (extra-cell)           | 1                   |
+-----------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import validate

report = validate('capital.resource.yaml')
print(report.to_summary())
```
```text title="Validation Report: capital.resource.yaml"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-----------------------------------+---------------------+
| Description                       | Size/Name/Count     |
+===================================+=====================+
| File name                         | capital-invalid.csv |
+-----------------------------------+---------------------+
| File size (bytes)                 | 171                 |
+-----------------------------------+---------------------+
| Total Time Taken (sec)            | 0.007               |
+-----------------------------------+---------------------+
| Total Errors                      | 5                   |
+-----------------------------------+---------------------+
| Duplicate Label (duplicate-label) | 1                   |
+-----------------------------------+---------------------+
| Missing Cell (missing-cell)       | 1                   |
+-----------------------------------+---------------------+
| Blank Row (blank-row)             | 1                   |
+-----------------------------------+---------------------+
| Type Error (type-error)           | 1                   |
+-----------------------------------+---------------------+
| Extra Cell (extra-cell)           | 1                   |
+-----------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
</Tabs>

Okay, why do we need to use a resource descriptor if the result is the same? The reason is metadata + data packaging. Let's extend our resource descriptor to show how you can edit and validate metadata:

```python script title="Python"
from frictionless import describe

resource = describe('capital-invalid.csv')
resource['bytes'] = 100 # this is wrong
resource['hash'] = 'ae23c74693ca2d3f0e38b9ba3570775b' # this is a made up incorrect hash
resource.to_yaml('capital.resource.yaml')
```

We have added a few incorrect, made up attributes to our resource descriptor as an example. Now, the validation below reports these errors in addition to all the errors we had before. This example shows how concepts like Data Resource can be extremely useful when working with data.

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless validate capital.resource.yaml
```
```text title="Validation Report: capital.resource.yaml"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-------------------------------------+---------------------+
| Description                         | Size/Name/Count     |
+=====================================+=====================+
| File name                           | capital-invalid.csv |
+-------------------------------------+---------------------+
| File size (bytes)                   | 171                 |
+-------------------------------------+---------------------+
| Total Time Taken (sec)              | 0.008               |
+-------------------------------------+---------------------+
| Total Errors                        | 7                   |
+-------------------------------------+---------------------+
| Duplicate Label (duplicate-label)   | 1                   |
+-------------------------------------+---------------------+
| Missing Cell (missing-cell)         | 1                   |
+-------------------------------------+---------------------+
| Blank Row (blank-row)               | 1                   |
+-------------------------------------+---------------------+
| Type Error (type-error)             | 1                   |
+-------------------------------------+---------------------+
| Extra Cell (extra-cell)             | 1                   |
+-------------------------------------+---------------------+
| Hash Count Error (hash-count-error) | 1                   |
+-------------------------------------+---------------------+
| Byte Count Error (byte-count-error) | 1                   |
+-------------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
|       |         | hash-      | The data source does not match the expected hash |
|       |         | count-     | count: expected md5 is                           |
|       |         | error      | "ae23c74693ca2d3f0e38b9ba3570775b" and actual is |
|       |         |            | "dcdeae358cfd50860c18d953e021f836"               |
+-------+---------+------------+--------------------------------------------------+
|       |         | byte-      | The data source does not match the expected byte |
|       |         | count-     | count: expected is "100" and actual is "171"     |
|       |         | error      |                                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import validate

report = validate('capital.resource.yaml')
print(report.to_summary())
```
```text title="Validation Report: capital.resource.yaml"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-------------------------------------+---------------------+
| Description                         | Size/Name/Count     |
+=====================================+=====================+
| File name                           | capital-invalid.csv |
+-------------------------------------+---------------------+
| File size (bytes)                   | 171                 |
+-------------------------------------+---------------------+
| Total Time Taken (sec)              | 0.011               |
+-------------------------------------+---------------------+
| Total Errors                        | 7                   |
+-------------------------------------+---------------------+
| Duplicate Label (duplicate-label)   | 1                   |
+-------------------------------------+---------------------+
| Missing Cell (missing-cell)         | 1                   |
+-------------------------------------+---------------------+
| Blank Row (blank-row)               | 1                   |
+-------------------------------------+---------------------+
| Type Error (type-error)             | 1                   |
+-------------------------------------+---------------------+
| Extra Cell (extra-cell)             | 1                   |
+-------------------------------------+---------------------+
| Hash Count Error (hash-count-error) | 1                   |
+-------------------------------------+---------------------+
| Byte Count Error (byte-count-error) | 1                   |
+-------------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
|       |         | hash-      | The data source does not match the expected hash |
|       |         | count-     | count: expected md5 is                           |
|       |         | error      | "ae23c74693ca2d3f0e38b9ba3570775b" and actual is |
|       |         |            | "dcdeae358cfd50860c18d953e021f836"               |
+-------+---------+------------+--------------------------------------------------+
|       |         | byte-      | The data source does not match the expected byte |
|       |         | count-     | count: expected is "100" and actual is "171"     |
|       |         | error      |                                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
</Tabs>

## Validating a Package

A package is a set of resources + additional metadata. To showcase a package validation we need to use one more tabular file:

> Download [`capital-valid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-valid.csv) to reproduce the examples (right-click and "Save link as").

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
cat capital-valid.csv
```
```text title="Data: capital-valid.csv"
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

</TabItem>
<TabItem value="python">

```python script
with open('capital-valid.csv') as file:
    print(file.read())
```
```text title="Data: capital-valid.csv"
id,name
1,London
2,Berlin
3,Paris
4,Madrid
5,Rome
```

</TabItem>
</Tabs>

Now let's describe and validate a package which contains the data files we have seen so far:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless describe capital-*id.csv > capital.package.yaml
frictionless validate capital.package.yaml
```
```text title="Validation Report: capital.package.yaml"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-----------------------------------+---------------------+
| Description                       | Size/Name/Count     |
+===================================+=====================+
| File name                         | capital-invalid.csv |
+-----------------------------------+---------------------+
| File size (bytes)                 | 171                 |
+-----------------------------------+---------------------+
| Total Time Taken (sec)            | 0.005               |
+-----------------------------------+---------------------+
| Total Errors                      | 5                   |
+-----------------------------------+---------------------+
| Duplicate Label (duplicate-label) | 1                   |
+-----------------------------------+---------------------+
| Missing Cell (missing-cell)       | 1                   |
+-----------------------------------+---------------------+
| Blank Row (blank-row)             | 1                   |
+-----------------------------------+---------------------+
| Type Error (type-error)           | 1                   |
+-----------------------------------+---------------------+
| Extra Cell (extra-cell)           | 1                   |
+-----------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+


# -----
# valid: capital-valid.csv 
# -----

## Summary 

+------------------------+-------------------+
| Description            | Size/Name/Count   |
+========================+===================+
| File name              | capital-valid.csv |
+------------------------+-------------------+
| File size (bytes)      | 50                |
+------------------------+-------------------+
| Total Time Taken (sec) | 0.004             |
+------------------------+-------------------+
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import describe, validate

# create package descriptor
package = describe("capital-*id.csv")
package.to_yaml("capital.package.yaml")
# validate
report = validate("capital.package.yaml")
print(report.to_summary())
```
```text title="Validation Report: capital.package.yaml"
# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-----------------------------------+---------------------+
| Description                       | Size/Name/Count     |
+===================================+=====================+
| File name                         | capital-invalid.csv |
+-----------------------------------+---------------------+
| File size (bytes)                 | 171                 |
+-----------------------------------+---------------------+
| Total Time Taken (sec)            | 0.005               |
+-----------------------------------+---------------------+
| Total Errors                      | 5                   |
+-----------------------------------+---------------------+
| Duplicate Label (duplicate-label) | 1                   |
+-----------------------------------+---------------------+
| Missing Cell (missing-cell)       | 1                   |
+-----------------------------------+---------------------+
| Blank Row (blank-row)             | 1                   |
+-----------------------------------+---------------------+
| Type Error (type-error)           | 1                   |
+-----------------------------------+---------------------+
| Extra Cell (extra-cell)           | 1                   |
+-----------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+


# -----
# valid: capital-valid.csv 
# -----

## Summary 

+------------------------+-------------------+
| Description            | Size/Name/Count   |
+========================+===================+
| File name              | capital-valid.csv |
+------------------------+-------------------+
| File size (bytes)      | 50                |
+------------------------+-------------------+
| Total Time Taken (sec) | 0.004             |
+------------------------+-------------------+
```

</TabItem>
</Tabs>

As we can see, the result is in a similar format to what we have already seen, and shows errors as we expected: we have one invalid resource and one valid resource.

## Validating an Inquiry

> The Inquiry is an advanced concept mostly used by software integrators. For example, under the hood, Frictionless Framework uses inquiries to implement client-server validation within the built-in API. Please skip this section if this information feels unnecessary for you.

Inquiry is a declarative representation of a validation job. It gives you an ability to create, export, and share arbitrary validation jobs containing a set of individual validation tasks. Tasks in the Inquiry accept the same arguments written in camelCase as the corresponding `validate` functions.

Let's create an Inquiry that includes an individual file validation and a resource validation. In this example we will use the data file, `capital-valid.csv` and the resource, `capital.resource.json` which describes the invalid data file we have already seen:

```python script title="Python"
from frictionless import Inquiry

inquiry = Inquiry({'tasks': [
  {'source': 'capital-valid.csv'},
  {'source': 'capital.resource.yaml'},
]})
inquiry.to_yaml('capital.inquiry.yaml')
```
As usual, let's run validation:

<Tabs
defaultValue="cli"
values={[{ label: 'CLI', value: 'cli'}, { label: 'Python', value: 'python'}]}>
<TabItem value="cli">

```bash script
frictionless validate capital.inquiry.yaml
```
```text title="Validation Report: capital.inquiry.yaml"
# -----
# valid: capital-valid.csv 
# -----

## Summary 

+------------------------+-----------------------+
| Description            | Size/Name/Count       |
+========================+=======================+
| File name              | capital-valid.csv |
+------------------------+-----------------------+
| File size (bytes)      | 50                    |
+------------------------+-----------------------+
| Total Time Taken (sec) | 0.006                 |
+------------------------+-----------------------+


# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-------------------------------------+---------------------+
| Description                         | Size/Name/Count     |
+=====================================+=====================+
| File name                           | capital-invalid.csv |
+-------------------------------------+---------------------+
| File size (bytes)                   | 171                 |
+-------------------------------------+---------------------+
| Total Time Taken (sec)              | 0.006               |
+-------------------------------------+---------------------+
| Total Errors                        | 7                   |
+-------------------------------------+---------------------+
| Duplicate Label (duplicate-label)   | 1                   |
+-------------------------------------+---------------------+
| Missing Cell (missing-cell)         | 1                   |
+-------------------------------------+---------------------+
| Blank Row (blank-row)               | 1                   |
+-------------------------------------+---------------------+
| Type Error (type-error)             | 1                   |
+-------------------------------------+---------------------+
| Extra Cell (extra-cell)             | 1                   |
+-------------------------------------+---------------------+
| Hash Count Error (hash-count-error) | 1                   |
+-------------------------------------+---------------------+
| Byte Count Error (byte-count-error) | 1                   |
+-------------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
|       |         | hash-      | The data source does not match the expected hash |
|       |         | count-     | count: expected md5 is                           |
|       |         | error      | "ae23c74693ca2d3f0e38b9ba3570775b" and actual is |
|       |         |            | "dcdeae358cfd50860c18d953e021f836"               |
+-------+---------+------------+--------------------------------------------------+
|       |         | byte-      | The data source does not match the expected byte |
|       |         | count-     | count: expected is "100" and actual is "171"     |
|       |         | error      |                                                  |
+-------+---------+------------+--------------------------------------------------+


# -----
# valid: capital-valid.csv 
# -----

## Summary 

+------------------------+-------------------+
| Description            | Size/Name/Count   |
+========================+===================+
| File name              | capital-valid.csv |
+------------------------+-------------------+
| File size (bytes)      | 50                |
+------------------------+-------------------+
| Total Time Taken (sec) | 0.004             |
+------------------------+-------------------+
```

</TabItem>
<TabItem value="python">

```python script
from frictionless import validate

report = validate("capital.inquiry.yaml")
print(report.to_summary())
```
```text title="Validation Report: capital.inquiry.yaml"
# -----
# valid: capital-valid.csv 
# -----

## Summary 

+------------------------+-----------------------+
| Description            | Size/Name/Count       |
+========================+=======================+
| File name              | capital-valid.csv |
+------------------------+-----------------------+
| File size (bytes)      | 50                    |
+------------------------+-----------------------+
| Total Time Taken (sec) | 0.007                 |
+------------------------+-----------------------+


# -------
# invalid: capital-invalid.csv 
# -------

## Summary 

+-------------------------------------+---------------------+
| Description                         | Size/Name/Count     |
+=====================================+=====================+
| File name                           | capital-invalid.csv |
+-------------------------------------+---------------------+
| File size (bytes)                   | 171                 |
+-------------------------------------+---------------------+
| Total Time Taken (sec)              | 0.007               |
+-------------------------------------+---------------------+
| Total Errors                        | 7                   |
+-------------------------------------+---------------------+
| Duplicate Label (duplicate-label)   | 1                   |
+-------------------------------------+---------------------+
| Missing Cell (missing-cell)         | 1                   |
+-------------------------------------+---------------------+
| Blank Row (blank-row)               | 1                   |
+-------------------------------------+---------------------+
| Type Error (type-error)             | 1                   |
+-------------------------------------+---------------------+
| Extra Cell (extra-cell)             | 1                   |
+-------------------------------------+---------------------+
| Hash Count Error (hash-count-error) | 1                   |
+-------------------------------------+---------------------+
| Byte Count Error (byte-count-error) | 1                   |
+-------------------------------------+---------------------+

## Errors 

+-------+---------+------------+--------------------------------------------------+
| row   | field   | code       | message                                          |
+=======+=========+============+==================================================+
|       | 3       | duplicate- | Label "name" in the header at position "3" is    |
|       |         | label      | duplicated to a label: at position "2"           |
+-------+---------+------------+--------------------------------------------------+
| 10    | 3       | missing-   | Row at position "10" has a missing cell in field |
|       |         | cell       | "name2" at position "3"                          |
+-------+---------+------------+--------------------------------------------------+
| 11    |         | blank-row  | Row at position "11" is completely blank         |
+-------+---------+------------+--------------------------------------------------+
| 12    | 1       | type-error | Type error in the cell "x" in row "12" and field |
|       |         |            | "id" at position "1": type is "integer/default"  |
+-------+---------+------------+--------------------------------------------------+
| 12    | 4       | extra-cell | Row at position "12" has an extra value in field |
|       |         |            | at position "4"                                  |
+-------+---------+------------+--------------------------------------------------+
|       |         | hash-      | The data source does not match the expected hash |
|       |         | count-     | count: expected md5 is                           |
|       |         | error      | "ae23c74693ca2d3f0e38b9ba3570775b" and actual is |
|       |         |            | "dcdeae358cfd50860c18d953e021f836"               |
+-------+---------+------------+--------------------------------------------------+
|       |         | byte-      | The data source does not match the expected byte |
|       |         | count-     | count: expected is "100" and actual is "171"     |
|       |         | error      |                                                  |
+-------+---------+------------+--------------------------------------------------+
```

</TabItem>
</Tabs>

At first sight, it might not be clear why such a construct exists, but when your validation workflow gets complex, the Inquiry can provide a lot of flexibility and power.

> The Inquiry will use multiprocessing if there is the `parallel` flag provided. It might speed up your validation dramatically especially on a 4+ cores processor.

## Validation Report

All the `validate` functions return a Validation Report. This is a unified object containing information about a validation: source details, the error, etc. Let's explore a report:

```python script title="Python"
from pprint import pprint
from frictionless import validate

report = validate('capital-invalid.csv', pick_errors=['duplicate-label'])
pprint(report)
```
```
{'errors': [],
 'stats': {'errors': 1, 'tasks': 1},
 'tasks': [{'errors': [{'code': 'duplicate-label',
                        'description': 'Two columns in the header row have the '
                                       'same value. Column names should be '
                                       'unique.',
                        'fieldName': 'name2',
                        'fieldNumber': 3,
                        'fieldPosition': 3,
                        'label': 'name',
                        'labels': ['id', 'name', 'name'],
                        'message': 'Label "name" in the header at position "3" '
                                   'is duplicated to a label: at position "2"',
                        'name': 'Duplicate Label',
                        'note': 'at position "2"',
                        'rowPositions': [1],
                        'tags': ['#table', '#header', '#label']}],
            'partial': False,
            'resource': {'encoding': 'utf-8',
                         'format': 'csv',
                         'hashing': 'md5',
                         'name': 'capital-invalid',
                         'path': 'capital-invalid.csv',
                         'profile': 'tabular-data-resource',
                         'schema': {'fields': [{'name': 'id',
                                                'type': 'integer'},
                                               {'name': 'name',
                                                'type': 'string'},
                                               {'name': 'name2',
                                                'type': 'string'}]},
                         'scheme': 'file',
                         'stats': {'bytes': 171,
                                   'fields': 3,
                                   'hash': 'dcdeae358cfd50860c18d953e021f836',
                                   'rows': 11}},
            'scope': ['duplicate-label'],
            'stats': {'errors': 1},
            'time': 0.028,
            'valid': False}],
 'time': 0.028,
 'valid': False,
 'version': '4.1.0'}
```

As we can see, there is a lot of information; you can find a detailed description of the Validation Report in the [API Reference](../references/api-reference.md#report). Errors are grouped by tasks (i.e. data files); for some validation there can be dozens of tasks. Let's use the `report.flatten` function to simplify the representation of errors. This function helps to represent a report as a list of errors:

```python script title="Python"
from pprint import pprint
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "message"]))
```
```
[[None,
  3,
  'duplicate-label',
  'Label "name" in the header at position "3" is duplicated to a label: at '
  'position "2"']]
```

In some situations, an error can't be associated with a task; then it goes to the top-level `report.errors` property:

```python script title="Python"
from pprint import pprint
from frictionless import validate_schema

report = validate_schema("bad.json")
pprint(report)
```
```
{'errors': [{'code': 'schema-error',
             'description': 'Provided schema is not valid.',
             'message': 'Schema is not valid: cannot extract metadata '
                        '"bad.json" because "[Errno 2] No such file or '
                        'directory: \'bad.json\'"',
             'name': 'Schema Error',
             'note': 'cannot extract metadata "bad.json" because "[Errno 2] No '
                     'such file or directory: \'bad.json\'"',
             'tags': []}],
 'stats': {'errors': 1, 'tasks': 0},
 'tasks': [],
 'time': 0.0,
 'valid': False,
 'version': '4.1.0'}
```

## Validation Errors

The Error object is at the heart of the validation process. The Report has `report.errors` and `report.tasks[].errors`, properties that can contain the Error object. Let's explore it by taking a deeper look at the `duplicate-label` error:

```python script title="Python"
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
error = report.task.error  # this is only available for one table / one error sitution
print(f'Code: "{error.code}"')
print(f'Name: "{error.name}"')
print(f'Tags: "{error.tags}"')
print(f'Note: "{error.note}"')
print(f'Message: "{error.message}"')
print(f'Description: "{error.description}"')
```
```
Code: "duplicate-label"
Name: "Duplicate Label"
Tags: "['#table', '#header', '#label']"
Note: "at position "2""
Message: "Label "name" in the header at position "3" is duplicated to a label: at position "2""
Description: "Two columns in the header row have the same value. Column names should be unique."
```

Above, we have listed universal error properties. Depending on the type of an error there can be additional ones. For example, for our `duplicate-label` error:

```python script title="Python"
from pprint import pprint
from frictionless import validate

report = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
error = report.task.error  # this is only available for one table / one error sitution
pprint(error)
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

There are various validation checks included in the core Frictionless Framework along with an ability to create custom checks. You can provide a list of checks where individual checks are in the form of:
- a dict: `{'code': 'code', 'option1': 'value1'}`
- an object: `checks.code(option1='value1')`

See [Validation Checks](validation-checks.md) for a list of available checks.

```python script title="Python"
from pprint import pprint
from frictionless import validate, checks

checks = [checks.sequential_value(field_name='id')]
report = validate('capital-invalid.csv', checks=checks)
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "note"]))
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

```python script title="Python"
from pprint import pprint
from frictionless import validate, errors

# Create check
def forbidden_two(row):
    if row['header'] == 2:
        note = '2 is forbidden!'
        yield errors.CellError.from_row(row, note=note, field_name='header')

# Validate table
source = b'header\n1\n2\n3'
report = validate(source,  format='csv', checks=[forbidden_two])
pprint(report.flatten(["rowPosition", "fieldPosition", "code", "note"]))
```
```
[[3, 1, 'cell-error', '2 is forbidden!']]
```

Usually, it also makes sense to create a custom error for your custom check. The Check class provides other useful methods like `validate_header` etc. Please read the [API Reference](../references/api-reference.md) for more details.

Learn more about custom checks in the [Check Guide](extension/check-guide.md).

## Pick/Skip Errors

We can pick or skip errors by providing a list of error codes. This is useful when you already know your data has some errors, but you want to ignore them for now. For instance, if you have a data table with repeating header names. Let's see an example of how to pick and skip errors:

```python script title="Python"
from pprint import pprint
from frictionless import validate

report1 = validate("capital-invalid.csv", pick_errors=["duplicate-label"])
report2 = validate("capital-invalid.csv", skip_errors=["duplicate-label"])
pprint(report1.flatten(["rowPosition", "fieldPosition", "code"]))
pprint(report2.flatten(["rowPosition", "fieldPosition", "code"]))
```
```
[[None, 3, 'duplicate-label']]
[[10, 3, 'missing-cell'],
 [11, None, 'blank-row'],
 [12, 1, 'type-error'],
 [12, 4, 'extra-cell']]
```

It's also possible to use error tags (for more information please consult the [Errors Reference](../references/errors-reference.md)):

```python script title="Python"
from pprint import pprint
from frictionless import validate

report1 = validate("capital-invalid.csv", pick_errors=["#header"])
report2 = validate("capital-invalid.csv", skip_errors=["#row"])
pprint(report1.flatten(["rowPosition", "fieldPosition", "code"]))
pprint(report2.flatten(["rowPosition", "fieldPosition", "code"]))
```
```
[[None, 3, 'duplicate-label']]
[[None, 3, 'duplicate-label']]
```

## Limit Errors

This option allows you to limit the amount of errors, and can be used when you need to do a quick check or want to "fail fast". For instance, here we use `limit_errors` to find just the 1st error and add it to our report:

```python script title="Python"
from pprint import pprint
from frictionless import validate

report = validate("capital-invalid.csv", limit_errors=1)
pprint(report.flatten(["rowPosition", "fieldPosition", "code"]))
```
```
[[None, 3, 'duplicate-label']]
```

## Limit Memory

Frictionless is a streaming engine; usually it is possible to validate terabytes of data with basically O(1) memory consumption. It means that memory usage doesn't depend on the size of your data making the validation infinitely scalable. For some validation, this is not the case because Frctionless needs to buffer some cells e.g. to check uniqueness. Here memory management can be handy.

The default memory limit is 1000MB. You can adjust this based on your exact use case. For example, if you're running Frictionless as an API server you might reduce the memory usage. If a validation hits the limit it will not raise a failure - it will return a report with a task error:

```python title="Python"
from frictionless import validate

source = lambda: ([integer] for integer in range(1, 100000000))
schema = {"fields": [{"name": "integer", "type": "integer"}], "primaryKey": "integer"}
report = validate(source, layout={'header': False}, schema=schema, limit_memory=50)
print(report.flatten(["code", "note"]))
```
```
[['task-error', 'exceeded memory limit "50MB"']]
```
