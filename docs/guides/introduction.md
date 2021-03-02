---
title: Introduction
---

[![Build](https://img.shields.io/github/workflow/status/frictionlessdata/frictionless-py/general/master)](https://github.com/frictionlessdata/frictionless-py/actions)
[![Coverage](https://img.shields.io/codecov/c/github/frictionlessdata/frictionless-py/master)](https://codecov.io/gh/frictionlessdata/frictionless-py)
[![Registry](https://img.shields.io/pypi/v/frictionless.svg)](https://pypi.python.org/pypi/frictionless)
[![Codebase](https://img.shields.io/badge/github-master-brightgreen)](https://github.com/frictionlessdata/frictionless-py)
[![Support](https://img.shields.io/badge/chat-discord-brightgreen)](https://discord.com/channels/695635777199145130/695635777199145133)

> Frictionless@4 is now live! Please read the [migration guide](https://framework.frictionlessdata.io/docs/development/migration)

Frictionless is a framework to describe, extract, validate, and transform tabular data (DEVT Framework). It supports a great deal of data schemes and formats, and provides popular platforms integrations. The framework is powered by the lightweight yet comprehensive [Frictionless Data Specifications](https://specs.frictionlessdata.io/).

## Why Frictionless Data?

Generating insight and conclusions from data is often not a straightforward process. Data can be poorly structured, hard to find, archived in difficult to use formats, or incomplete. These issues create “friction” and make it difficult to use, publish and share data. The Frictionless Data project aims to reduce frictions while working with data, with a goal to make it effortless to transport data among different tools and platforms for further analysis. This project is a suite of open source software, tools, and specifications focused on improving data and metadata interoperability. The core software library is [Frictionless-py](https://github.com/frictionlessdata/frictionless-py), and this documentation will help you learn how to use this Frictionless Framework. Are you interested in learning more about the project as a whole? Read the overview section below.

## Frictionless Specifications

The core of the Framework are the Frictionless Specifications. These specifications are a set of patterns for describing data including Data Package (for datasets), Data Resource (for files) and Table Schema (for tables). A Data Package is a simple container format used to describe and package a collection of data and metadata, including schemas. Frictionless-py lets users create data packages and schemas that conform to the Frictionless specifications.
You can read more about the Frictionless specifications at https://specs.frictionlessdata.io/.

## Frictionless Framework

The Frictionless Framework makes data more usable by generating metadata and schemas and by validating data to ensure quality. There are four main functions that can be used independently to improve your data: Describe data, Extract data, Validate data, and Transform data (DEVT). Here, we will go into more detail on each of these main functions.

**<big>Describe your data:</big>** infer and edit metadata from a data file. For instance, `describe` will generate metadata describing the layout of the data (i.e. which row is the header) as well as a schema describing the data contents (i.e. the type of data in a column). This is a first step for ensuring data quality and usability.

**<big>Extract your data:</big>** read and normalize data from a data file. By default, `extract` returns data conforming to the metadata that was either defined in the `describe` step or inferred automatically. The user can opt-out of this to get the raw (unnormalized) data. Frictionless supports various file schemes like HTTP, FTP, and S3 and data formats like CSV, XLS, JSON, SQL, and others.

**<big>Validate your data:</big>** detect errors in a data file. `validate` runs checks on data tables, resources, and datasets to identify potential issues (i.e. are there any missing values?). These checks can be modified and can be based on a provided schema. While `extract` cleans the data by removing the invalid cells, `validate` helps to see the whole picture of the raw file.

**<big>Transform your data:</big>** change a data file's metadata and data. This step can including reshaping data, saving it in a different format, or uploading the data somewhere. Frictionless provides a pipeline capability and a lower-level interface to work with the data.

## Important Features

Frictionless is a complete data solution providing rich functionality. It's hard to list all the features it provides, but here are the most important ones:

- Open Source (MIT)
- Powerful Python framework
- Convenient command-line interface
- Low memory consumption for data of any size
- Reasonable performance on big data
- Support for compressed files
- Custom checks and formats
- Fully pluggable architecture
- An included API server
- More than 1000+ tests

## Usage Example

Frictionless can be run on CLI, in Python, and even as an API server. Here is a short example to get started with the framework:

> Download [`invalid.csv`](https://raw.githubusercontent.com/frictionlessdata/frictionless-py/master/data/invalid.csv) into the `data` folder to reproduce the examples

```bash title="CLI"
pip install frictionless
frictionless validate data/invalid.csv
```
```yaml
# -------
# invalid: data/invalid.csv
# -------

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

## User Stories

> TODO: Add visual diagrams here

Frictionless is a DEVT-framework (describe-extract-validate-transform). In contrast to ETL-frameworks (extract-transform-load), Frictionless does not have a linear flow. For example, let’s look at some user stories:

- I want to quickly clean my data file:
  - [D] Describe (optional)
  - [E] Extract
- I want to explore my data file:
  - [D] Describe (optional)
  - [E] Extract (in the raw-data mode)
- I want to find errors in my data and clean it manually:
  - [D] Describe (optional)
  - [V] Validate
- I want to share my data file with metadata:
  - [D] Describe
  - [T] Transform (optional)
- I want to export my file into a different format:
  - [D] Describe (optional)
  - [T] Transform
- I want to reshape my file:
  - [D] Describe (optional)
  - [T] Transform
