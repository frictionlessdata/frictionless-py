---
title: Quick Start
---

Let's get started with Frictionless! We will learn how to install and use the framework. The simple example below will showcase the framework's basic functionality. For an introduction to concepts behind the Frictionless Framework, please read the [Frictionless Introduction](introduction.md).

## Installation

> The framework requires Python3.6+. Versioning follows the [SemVer Standard](https://semver.org/)

```bash title="CLI"
pip install frictionless
pip install frictionless[sql] # to install a core plugin (optional)
```

The framework supports CSV, Excel, and JSON formats by default. Please use the command above to install a core plugin and add support for SQL, Pandas, HTML, and others (check the [list of Frictionless Framework plugins and their status](https://framework.frictionlessdata.io/docs/references/plugins-reference)). Usually, you don't need to think about it in advance–frictionless will display a useful error message about a missing plugin with installation instructions.

### Troubleshooting

Did you have an error installing Frictionless? Here are some dependencies and common errors:
- `pip: command not found`. Please see the [pip docs](https://pip.pypa.io/en/stable/installing/) for help installing pip.
- [Installing Python help (Mac)](https://docs.python.org/3/using/mac.html)
- [Installing Python help (Windows)](https://docs.python.org/3/using/windows.html)

Still having a problem? Ask us for help on our [Discord](https://discord.com/invite/j9DNFNw) chat or open an [issue](https://github.com/frictionlessdata/frictionless-py/issues). We're happy to help!

## Usage

The framework can be used:
- as a Python library
- as a command-line interface
- as a restful API server (for advanced use cases)

For instance, all the examples below do the same thing:

```python title="Python"
from frictionless import extract
rows = extract('data/table.csv')
```

```bash title="CLI"
frictionless extract data/table.csv
```

```text title="API"
[POST] /extract {"source': 'data/table.csv"}
```

All these interfaces are as much alike as possible regarding naming conventions and the way you interact with them. Usually, it's straightforward to translate, for instance, Python code to a command-line call. Frictionless provides code completion for Python and the command-line, which should help to get useful hints in real time. You can find the API reference [here](../references/api-reference.md).

Arguments conform to the following naming convention:
- for Python interfaces, they are snake_cased, e.g. `missing_values`
- within dictionaries or JSON objects, they are camelCased, e.g. `missingValues`
- in the command line, they use dashes, e.g. `--missing-values`

To get the documentation for a command-line interface just use the `--help` flag:

```bash title="CLI"
frictionless --help
frictionless describe --help
frictionless extract --help
frictionless validate --help
frictionless transform --help
```

## Example

> For more examples, use the [Basic Examples](basic-examples.md)

We will take a very messy data file:

> Download [`invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/invalid.csv) into the `data` folder to reproduce the examples

```bash title="CLI"
cat data/invalid.csv
```
```csv title="data/invalid.csv"
id,name,,name
1,english
1,english

2,german,1,2,3
```

First of all, let's use `describe` to infer the metadata directly from the tabular data. We can then edit and save it to provide others with useful information about the data:

> This output is in [YAML](https://yaml.org/), it is a default Frictionless output format.

```bash title="CLI"
frictionless describe data/invalid.csv
```
```yaml
# --------
# metadata: data/invalid.csv
# --------

encoding: utf-8
format: csv
scheme: file
hashing: md5
name: invalid
path: data/invalid.csv
profile: tabular-data-resource
schema:
  fields:
    - name: id
      type: integer
    - name: name
      type: string
    - name: field3
      type: integer
    - name: name2
      type: integer
```

Now that we have inferred a table schema from the data file (e.g., expected format of the table, expected type of each value in a column, etc.), we can use `extract` to read the normalized tabular data from the source CSV file:

```bash title="CLI"
frictionless extract data/invalid.csv
```
```yaml
# ----
# data: data/invalid.csv
# ----

====  =======  ======  =====
id    name     field3  name2
====  =======  ======  =====
   1  english  None    None
   1  english  None    None
None  None     None    None
   2  german        1      2
====  =======  ======  =====
```

Last but not least, let's get a validation report. This report will help us to identify and fix all the errors present in the tabular data, as comprehensive information is provided for every problem:


```bash title="CLI"
frictionless validate data/invalid.csv
```
```yaml
# -------
# invalid: data/invalid.csv
# -------

====  =====  ===============  ====================================================================================
row   field  code             message
====  =====  ===============  ====================================================================================
None      3  blank-label      Label in the header in field at position "3" is blank
None      4  duplicate-label  Label "name" in the header at position "4" is duplicated to a label: at position "2"
   2      3  missing-cell     Row at position "2" has a missing cell in field "field3" at position "3"
   2      4  missing-cell     Row at position "2" has a missing cell in field "name2" at position "4"
   3      3  missing-cell     Row at position "3" has a missing cell in field "field3" at position "3"
   3      4  missing-cell     Row at position "3" has a missing cell in field "name2" at position "4"
   4  None   blank-row        Row at position "4" is completely blank
   5      5  extra-cell       Row at position "5" has an extra value in field at position "5"
====  =====  ===============  ====================================================================================
```

Now that we have all this information:
- we can clean up the table to ensure the data quality
- we can use the metadata to describe and share the dataset
- we can include the validation into our workflow to guarantee the validity
- and much more: don't hesitate and read the following sections of the documentation!
