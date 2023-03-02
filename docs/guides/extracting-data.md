---
script:
  basepath: data
---

# Extracting Data

> This guide assumes basic familiarity with the Frictionless Framework. To learn more, please read the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction) and [Quick Start](https://framework.frictionlessdata.io/docs/guides/quick-start).

Extracting data means reading tabular data from a source. We can use various customizations for this process such as providing a file format, table schema, limiting fields or rows amount, and much more. This guide will discuss the main `extract` functions (`extract`, `extract_resource`, `extract_package`) and will then go into more advanced details about the `Resource Class`, `Package Class`, `Header Class`, and `Row Class`. The output from the extract function is in 'utf-8' encoding scheme.

Let's see this with some real files:

> Download [`country-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/country-3.csv) to reproduce the examples (right-click and "Save link as").

```bash script tabs=CLI
cat country-3.csv
```

```python script tabs=Python
with open('country-3.csv') as file:
    print(file.read())
```

> Download [`capital-3.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/capital-3.csv) to reproduce the examples (right-click and "Save link as").

```bash script tabs=CLI
cat capital-3.csv
```

```python script tabs=Python
with open('capital-3.csv') as file:
    print(file.read())
```

To start, we will extract data from a resource:

```bash script tabs=CLI
frictionless extract country-3.csv
```

```python script tabs=Python
from pprint import pprint
from frictionless import extract

rows = extract('country-3.csv')
pprint(rows)
```

## Extract Functions

The high-level interface for extracting data provided by Frictionless is a set of `extract` functions:
- `extract`: detects the source file type and extracts data accordingly
- `resource.extract`: returns a data table
- `package.extract`: returns a map of the package's tables

As described in more detail in the [Introduction](https://framework.frictionlessdata.io/docs/guides/introduction), a resource is a single file, such as a data file, and a package is a set of files, such as a data file and a schema.

The command/function would be used as follows:

```bash tabs=CLI
frictionless extract your-table.csv
frictionless extract your-resource.json --type resource
frictionless extract your-package.json --type package
```

```python tabs=Python
from frictionless import extract

rows = extract('capital-3.csv')
resource = extract('capital-3.csv', type="resource")
package = extract('capital-3.csv', type="package")
```

The `extract` functions always reads data in the form of rows, into memory. The lower-level interfaces will allow you to stream data, which you can read about in the [Resource Class](#resource-class) section below.

## Extracting a Resource

A resource contains only one file. To extract a resource, we have three options. First, we can use the same approach as above, extracting from the data file itself:

```bash script tabs=CLI
frictionless extract capital-3.csv
```

```python script tabs=Python
from pprint import pprint
from frictionless import extract

rows = extract('capital-3.csv')
pprint(rows)
```

Our second option is to extract the resource from a descriptor file by using the `extract_resource` function. A descriptor file is useful because it can contain different metadata and be stored on the disc.

As an example of how to use `extract_resource`, let's first create a descriptor file (note: this example uses YAML for the descriptor, but Frictionless also supports JSON):

```python script tabs=Python
from frictionless import Resource

resource = Resource('capital-3.csv')
resource.infer()
# as an example, in the next line we will append the schema
resource.schema.missing_values.append('3') # will interpret 3 as a missing value
resource.to_yaml('capital.resource-test.yaml') # use resource.to_json for JSON format
```
You can also use a pre-made descriptor file.

Now, this descriptor file can be used to extract the resource:

```bash script tabs=CLI
frictionless extract capital.resource-test.yaml
```

```python script tabs=Python
from pprint import pprint
from frictionless import extract

rows = extract('capital.resource.yaml')
pprint(rows)
```

So what has happened in this example? We set the textual representation of the number "3" to be a missing value. In the output we can see how the `id` number 3 now appears as `None` representing a missing value. This toy example demonstrates how the metadata in a descriptor can be used; other values like "NA" are more common for missing values.

You can read more advanced details about the [Resource Class below](#resource-class).

## Extracting a Package

The third way we can extract information is from a package, which is a set of two or more files, for instance, two data files and a corresponding metadata file.

As a primary example, we provide two data files to the `extract` command which will be enough to detect that it's a dataset. Let's start by using the command-line interface:


```bash script tabs=CLI
frictionless extract *-3.csv
```

```python script tabs=Python
from pprint import pprint
from frictionless import extract

data = extract('*-3.csv')
pprint(data)
```

We can also extract the package from a descriptor file using the `package.extract` function (Note: see the [Package Class section](#package-class) for the creation of the `country.package.yaml` file):

```bash script tabs=CLI
frictionless extract country.package.yaml
```

```python script tabs=Python
from frictionless import Package

package = Package('country.package.yaml')
pprint(package.extract())
```

You can read more advanced details about the [Package Class below](#package-class).

> The following sections contain further, advanced details about the `Resource Class`, `Package Class`, `Header Class`, and `Row Class`.

## Resource Class

The Resource class provides metadata about a resource with read and stream functions. The `extract` functions always read rows into memory; Resource can do the same but it also gives a choice regarding output data which can be `rows`, `data`, `text`, or `bytes`. Let's try reading all of them.

### Reading Bytes

It's a byte representation of the contents:

```python script tabs=Python
from pprint import pprint
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_bytes())
```

### Reading Text

It's a textual representation of the contents:

```python script tabs=Python
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_text())
```

### Reading Cells

For a tabular data there are raw representaion of the tabular contents:

```python script tabs=Python
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_cells())
```

### Reading Rows

For a tabular data there are row available which is are normalized lists presented as dictionaries:

```python script tabs=Python
from frictionless import Resource

resource = Resource('country-3.csv')
pprint(resource.read_rows())
```

### Reading a Header

For a tabular data there is the Header object available:

```python script tabs=Python
from frictionless import Resource

with Resource('country-3.csv') as resource:
    pprint(resource.header)
```

### Streaming Interfaces

It's really handy to read all your data into memory but it's not always possible if a file is very big. For such cases, Frictionless provides streaming functions:

```python tabs=Python
from frictionless import Resource

with Resource('country-3.csv') as resource:
    resource.byte_stream
    resource.text_stream
    resource.list_stream
    resource.row_stream
```

## Package Class

The Package class provides functions to read the contents of a package. First of all, let's create a package descriptor:

```bash script tabs=CLI
frictionless describe *-3.csv --json > country.package.json
```

```python script tabs=Python
from frictionless import describe

package = describe('*-3.csv')
package.to_json('country.package.json')
```

Note that --json is used here to output the descriptor in JSON format. Without this, the default output is in YAML format as we saw above.

We can create a package from data files (using their paths) and then read the package's resources:

```python script tabs=Python
from frictionless import Package

package = Package('*-3.csv')
pprint(package.get_resource('country-3').read_rows())
pprint(package.get_resource('capital-3').read_rows())
```

The package by itself doesn't provide any read functions directly because it's just a contrainer. You can select a pacakge's resource and use the Resource API from above for data reading.
