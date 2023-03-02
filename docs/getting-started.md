---
script:
  basepath: data
---

# Getting Started

Let's get started with Frictionless! We will learn how to install and use the framework. The simple example below will showcase the framework's basic functionality.

## Installation

> The framework requires Python3.8+. Versioning follows the [SemVer Standard](https://semver.org/).

```bash tabs=CLI
pip install frictionless
pip install frictionless[sql] # to install a core plugin (optional)
pip install 'frictionless[sql]' # for zsh shell
```

The framework supports CSV, Excel, and JSON formats by default. The second command above installs a plugin for SQL support. There are plugins for SQL, Pandas, HTML, and others (all supported plugins are listed in the "File Formats" and schemes in "File Schemes" menu). Usually, you don't need to think about it in advance–frictionless will display a useful error message about a missing plugin with installation instructions.

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

```bash tabs=CLI
frictionless extract data/table.csv
```

```python tabs=Python
from frictionless import extract

rows = extract('data/table.csv')
```

```json tabs=API
[POST] /extract {"path': 'data/table.csv"}
```

All these interfaces are as much alike as possible regarding naming conventions and the way you interact with them. Usually, it's straightforward to translate, for instance, Python code to a command-line call. Frictionless provides code completion for Python and the command-line, which should help to get useful hints in real time. You can find the API reference at the bottom of the respective page, for example: [Schema  API Reference](../../docs/framework/schema.html#reference).

Arguments conform to the following naming convention:
- for Python interfaces, they are snake_cased, e.g. `missing_values`
- within dictionaries or JSON objects, they are camelCased, e.g. `missingValues`
- in the command line, they use dashes, e.g. `--missing-values`

To get the documentation for a command-line interface just use the `--help` flag:

```bash tabs=CLI
frictionless --help
frictionless describe --help
frictionless extract --help
frictionless validate --help
frictionless transform --help
```

## Example

> Download [`invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/main/data/invalid.csv) to reproduce the examples (right-click and "Save link as"). For more examples, please take a look at the [Basic Examples](basic-examples.md) article.

We will take a very messy data file:

```bash script tabs=CLI
cat invalid.csv
```

```python script tabs=Python
with open('invalid.csv') as file:
    print(file.read())
```

First of all, let's use `describe` to infer the metadata directly from the tabular data. We can then edit and save it to provide others with useful information about the data:

> The CLI output is in [YAML](https://yaml.org/), it is a default Frictionless output format.

```bash script tabs=CLI output=yaml
frictionless describe invalid.csv
```

```python script tabs=Python output=python
from pprint import pprint
from frictionless import describe

resource = describe('invalid.csv')
pprint(resource)
```

Now that we have inferred a table schema from the data file (e.g., expected format of the table, expected type of each value in a column, etc.), we can use `extract` to read the normalized tabular data from the source CSV file:

```bash script tabs=CLI
frictionless extract invalid.csv
```

```python script tabs=Python output=python
from pprint import pprint
from frictionless import extract

rows = extract('invalid.csv')
pprint(rows)
```

Last but not least, let's get a validation report. This report will help us to identify and fix all the errors present in the tabular data, as comprehensive information is provided for every problem:

```bash script tabs=CLI
frictionless validate invalid.csv
```

```python script tabs=Python output=python
from pprint import pprint
from frictionless import validate

report = validate('invalid.csv')
pprint(report.flatten(["rowNumber", "fieldNumber", "type"]))
```

Now that we have all this information:
- we can clean up the table to ensure the data quality
- we can use the metadata to describe and share the dataset
- we can include the validation into our workflow to guarantee the validity
- and much more: don't hesitate and read the following sections of the documentation!
