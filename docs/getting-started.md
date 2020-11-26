# Getting Started

Let's get started with Frictionless! We will learn how to install and use the framework. The simple example below will showcase the framework's basic functionality.

## Installation

> Versioning follows the [SemVer Standard](https://semver.org/)

```
! pip install frictionless
# pip install frictionless[sql] - to install a core plugin
```

By default, the framework comes with the support of CSV, Excel, and JSON formats. Please use the command above to add support for SQL, Pandas, Html, and others. Usually, you don't need to think about it in advance - frictionless will show a useful error on a missing plugin with installation instruction.

## Usage

The framework can be used:
- as a Python library
- as a command-line interface
- as a restful API server

For example, all the examples below do the same thing:

```python
from frictionless import extract

rows = extract('data/table.csv')
# CLI: $ frictionless extract data/table.csv
# API: [POST] /extract {"source': 'data/table.csv"}
```

All these interfaces are close as much as possible regarding naming and the way you interact with them. Usually, it's straightforward to translate e.g., Python code to a command-line call. Frictionless provides code completion for Python and command-line, which should help to get useful hints in real-time.

Arguments follow this naming rule:
- for Python interfaces, they are lowercased, e.g. `missing_values`
- within dictionaries or JSON objects they are camel-cased, e.g. `missingValues`
- in a command line they use dashes, e.g. `--missing-values`

To get documentation for a command-line interface just use the `--help` flag:

```
$ frictionless --help
$ frictionless describe --help
$ frictionless extract --help
$ frictionless validate --help
$ frictionless transform --help
```

## Example

> All the examples use the data folder from this repository

We will take a very dirty data file:


```python
! cat data/invalid.csv
```

Firt of all, let's infer the metadata. We can save and edit it to provide useful information about the table:

> This output is in [YAML](https://yaml.org/), it is a default Frictionless output format.


```python
! frictionless describe data/invalid.csv
```

Secondly, we can extract a normalized data. It conforms to the inferred schema from above e.g., the dimension is fixed, and bad cells are omitted:


```python
! frictionless extract data/invalid.csv
```

Last but not least, let's get a validation report. This report will help us to fix all these errors as comprehensive information is provided for every tabular problem:


```python
! frictionless validate data/invalid.csv
```

Now having all this information:
- we can clean up the table to ensure the data quality
- we can use the metadata to describe and share the dataset
- we can include the validation into our workflow to guarantee the validity
- and much more: don't hesitate and read the following documentation!
