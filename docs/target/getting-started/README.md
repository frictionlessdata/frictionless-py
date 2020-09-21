# Getting Started

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1VyDx6C3pxF3Vab8MxH_sI86OTSNmYuDJ)



Let's get started with Frictionless! We will learn how to install and use the framework. The simple example below will showcase the framework's basic functionality.


## Installation

> Versioning follows the [SemVer Standard](https://semver.org/)





```bash
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



```bash
! wget -q -O invalid.csv https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/invalid.csv
```


```python
from frictionless import extract

rows = extract('invalid.csv')
# CLI: $ frictionless extract table.csv
# API: [POST] /extract {"source': 'table.csv"}
```

All these interfaces are close as much as possible regarding naming and the way you interact with them. Usually, it's straightforward to translate e.g., Python code to a command-line call. Frictionless provides code completion for Python and command-line, which should help to get useful hints in real-time.

Arguments follow this naming rule:
- for Python interfaces, they are lowercased, e.g. `missing_values`
- within dictionaries or JSON objects they are camel-cased, e.g. `missingValues`
- in a command line they use dashes, e.g. `--missing-values`

To get documentation for a command-line interface just use the `--help` flag:

```bash
$ frictionless --help
$ frictionless describe --help
$ frictionless extract --help
$ frictionless validate --help
$ frictionless transform --help
```


## Example

> All the examples use the data folder from this repository

We will take a very dirty data file:



```bash
! cat invalid.csv
```

    id,name,,name
    1,english
    1,english

    2,german,1,2,3


Firt of all, let's infer the metadata. We can save and edit it to provide useful information about the table:



```bash
! frictionless describe invalid.csv
```

    [metadata] invalid.csv

    bytes: 50
    compression: 'no'
    compressionPath: ''
    dialect: {}
    encoding: utf-8
    format: csv
    hash: 8c73c3d9d59088dcb2508e0b348bf8a8
    hashing: md5
    name: invalid
    path: invalid.csv
    profile: tabular-data-resource
    rows: 4
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
    scheme: file


Secondly, we can extract a normalized data. It conforms to the inferred schema from above e.g., the dimension is fixed, and bad cells are omitted:



```bash
! frictionless extract invalid.csv
```

    [data] invalid.csv

      id  name       field3    name2
    ----  -------  --------  -------
       1  english
       1  english

       2  german          1        2


Last but not least, let's get a validation report. This report will help us to fix all these errors as comprehensive information is provided for every tabular problem:



```bash
! frictionless validate invalid.csv
```

    [invalid] invalid.csv

      row    field  code              message
    -----  -------  ----------------  ------------------------------------------------------------------------------------------------
                 3  blank-header      Header in field at position "3" is blank
                 4  duplicate-header  Header "name" in field at position "4" is duplicated to header in another field: at position "2"
        2        3  missing-cell      Row at position "2" has a missing cell in field "field3" at position "3"
        2        4  missing-cell      Row at position "2" has a missing cell in field "name2" at position "4"
        3        3  missing-cell      Row at position "3" has a missing cell in field "field3" at position "3"
        3        4  missing-cell      Row at position "3" has a missing cell in field "name2" at position "4"
        4           blank-row         Row at position "4" is completely blank
        5        5  extra-cell        Row at position "5" has an extra value in field at position "5"


Now having all this information:
- we can clean up the table to ensure the data quality
- we can use the metadata to describe and share the dataset
- we can include the validation into our workflow to guarantee the validity
- and much more: don't hesitate and read the following documentation!
