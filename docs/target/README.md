# Frictionless Framework

[![Travis](https://img.shields.io/travis/frictionlessdata/frictionless-py/master.svg)](https://travis-ci.org/frictionlessdata/frictionless-py)
[![Coveralls](http://img.shields.io/coveralls/frictionlessdata/frictionless-py.svg?branch=master)](https://coveralls.io/r/frictionlessdata/frictionless-py?branch=master)
[![PyPi](https://img.shields.io/pypi/v/frictionless.svg)](https://pypi.python.org/pypi/frictionless)
[![Github](https://img.shields.io/badge/github-master-brightgreen)](https://github.com/frictionlessdata/frictionless-py)
[![Discord](https://img.shields.io/badge/chat-discord-brightgreen)](https://discord.com/channels/695635777199145130/695635777199145133)

Frictionless Framework is a framework to describe, extract, validate, and transform tabular data. It supports a great deal of data sources and formats, as well as provides popular platforms integrations. The framework is powered by the lightweight yet comprehensive [Frictionless Data Specifications](https://specs.frictionlessdata.io/).

> **[Important Notice]** We have renamed `goodtables` to `frictionless` since version 3. The framework got various improvements and was extended to be a complete data solution. The change in not breaking for the existing software so no actions are required. Please read the [Migration Guide](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/migration-guide/README.md) from `goodtables` to Frictionless Framework.
> - we continue to bug-fix `goodtables@2.x` in this [branch](https://github.com/frictionlessdata/goodtables-py/tree/goodtables) as well as it's available on [PyPi](https://pypi.org/project/goodtables/) as it was before
> - please note that `frictionless@3.x` version's API, we're working on at the moment, is not stable
> - we will release `frictionless@4.x` by the end of 2020 to be the first SemVer/stable version

## Purpose

- **Describe your data**: You can infer, edit and save metadata of your data tables. It's a first step for ensuring data quality and usability. Frictionless metadata includes general information about your data like textual description, as well as, field types and other tabular data details.
- **Extract your data**: You can read your data using a unified tabular interface. Data quality and consistency are guaranteed by a schema. Frictionless supports various file protocols like HTTP, FTP, and S3 and data formats like CSV, XLS, JSON, SQL, and others.
- **Validate your data**: You can validate data tables, resources, and datasets. Frictionless generates a unified validation report, as well as supports a lot of options to customize the validation process.
- **Transform your data**: You can clean, reshape, and transfer your data tables and datasets. Frictionless provides a pipeline capability and a lower-level interface to work with the data.

## Features

- Powerful Python framework
- Convenient command-line interface
- Low memory consumption for data of any size
- Reasonable performance on big data
- Support for compressed files
- Custom checks and formats
- Fully pluggable architecture
- The included API server
- More than 1000+ tests

## Example

```bash
$ frictionless validate data/invalid.csv
[invalid] data/invalid.csv

  row    field  code              message
-----  -------  ----------------  --------------------------------------------
             3  blank-header      Header in field at position "3" is blank
             4  duplicate-header  Header "name" in field "4" is duplicated
    2        3  missing-cell      Row "2" has a missing cell in field "field3"
    2        4  missing-cell      Row "2" has a missing cell in field "name2"
    3        3  missing-cell      Row "3" has a missing cell in field "field3"
    3        4  missing-cell      Row "3" has a missing cell in field "name2"
    4           blank-row         Row "4" is completely blank
    5        5  extra-cell        Row "5" has an extra value in field  "5"
```

## Documentation

- [Getting Started](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/getting-started/README.md)
- [Introduction Guide](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/introduction-guide/README.md)
- [Describing Data](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/describing-data/README.md)
- [Extracting Data](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/extracting-data/README.md)
- [Validating Data](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/validating-data/README.md)
- [Transforming Data](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/transforming-data/README.md)
- [Extension Guide](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/extension-guide/README.md)
- [Migration Guide](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/migration-guide/README.md)
- [Schemes Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/schemes-reference/README.md)
- [Formats Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/formats-reference/README.md)
- [Errors Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/errors-reference/README.md)
- [API Reference](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/api-reference/README.md)
- [Contributing](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/contributing/README.md)
- [Changelog](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/changelog/README.md)
- [Authors](https://github.com/frictionlessdata/frictionless-py/blob/master/docs/target/authors/README.md)
