# Frictionless Framework

[![Build](https://img.shields.io/github/workflow/status/frictionlessdata/frictionless-py/general/master)](https://github.com/frictionlessdata/frictionless-py/actions)
[![Coverage](https://img.shields.io/codecov/c/github/frictionlessdata/frictionless-py/master)](https://codecov.io/gh/frictionlessdata/frictionless-py)
[![Registry](https://img.shields.io/pypi/v/frictionless.svg)](https://pypi.python.org/pypi/frictionless)
[![Codebase](https://img.shields.io/badge/github-master-brightgreen)](https://github.com/frictionlessdata/frictionless-py)
[![Support](https://img.shields.io/badge/chat-discord-brightgreen)](https://discord.com/channels/695635777199145130/695635777199145133)

Frictionless is a framework to describe, extract, validate, and transform tabular data. It supports a great deal of data sources and formats, as well as provides popular platforms integrations. The framework is powered by the lightweight yet comprehensive [Frictionless Data Specifications](https://specs.frictionlessdata.io/).

> **[Important Notice]** We have renamed `goodtables` to `frictionless` since version 3. The framework got various improvements and was extended to be a complete data solution. The change in not breaking for the existing software so no actions are required. Please read the [Migration Guide](https://frictionlessdata.io/tooling/python/migration-guide/) from `goodtables` to Frictionless Framework.
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

### General

- [Getting Started](https://frictionlessdata.io/tooling/python/getting-started/)
- [Introduction Guide](https://frictionlessdata.io/tooling/python/introduction-guide/)
- [Describing Data](https://frictionlessdata.io/tooling/python/describing-data/)
- [Extracting Data](https://frictionlessdata.io/tooling/python/extracting-data/)
- [Validating Data](https://frictionlessdata.io/tooling/python/validating-data/)
- [Transforming Data](https://frictionlessdata.io/tooling/python/transforming-data/)
- [Extension Guide](https://frictionlessdata.io/tooling/python/extension-guide/)
- [Migration Guide](https://frictionlessdata.io/tooling/python/migration-guide/)
- [Schemes Reference](https://frictionlessdata.io/tooling/python/schemes-reference/)
- [Formats Reference](https://frictionlessdata.io/tooling/python/formats-reference/)
- [Errors Reference](https://frictionlessdata.io/tooling/python/errors-reference/)
- [API Reference](https://frictionlessdata.io/tooling/python/api-reference/)
- [Contributing](https://frictionlessdata.io/tooling/python/contributing/)
- [Changelog](https://frictionlessdata.io/tooling/python/changelog/)
- [Authors](https://frictionlessdata.io/tooling/python/authors/)

### Specific

- [Working with BigQuery](https://frictionlessdata.io/tooling/python/working-with-bigquery/)
- [Working with CKAN](https://frictionlessdata.io/tooling/python/working-with-ckan/)
- [Working with CSV](https://frictionlessdata.io/tooling/python/working-with-csv/)
- [Working with DataFlows](https://frictionlessdata.io/tooling/python/working-with-dataflows/)
- [Working with Excel](https://frictionlessdata.io/tooling/python/working-with-excel/)
- [Working with Filelike](https://frictionlessdata.io/tooling/python/working-with-filelike/)
- [Working with GSheets](https://frictionlessdata.io/tooling/python/working-with-gsheets/)
- [Working with HTML](https://frictionlessdata.io/tooling/python/working-with-html/)
- [Working with Inline](https://frictionlessdata.io/tooling/python/working-with-inline/)
- [Working with JSON](https://frictionlessdata.io/tooling/python/working-with-json/)
- [Working with Local](https://frictionlessdata.io/tooling/python/working-with-local/)
- [Working with Multipart](https://frictionlessdata.io/tooling/python/working-with-multipart/)
- [Working with ODS](https://frictionlessdata.io/tooling/python/working-with-ods/)
- [Working with Pandas](https://frictionlessdata.io/tooling/python/working-with-pandas/)
- [Working with Remote](https://frictionlessdata.io/tooling/python/working-with-remote/)
- [Working with S3](https://frictionlessdata.io/tooling/python/working-with-s3/)
- [Working with Server](https://frictionlessdata.io/tooling/python/working-with-server/)
- [Working with SPSS](https://frictionlessdata.io/tooling/python/working-with-spss/)
- [Working with SQL](https://frictionlessdata.io/tooling/python/working-with-sql/)
- [Working with Text](https://frictionlessdata.io/tooling/python/working-with-text/)
