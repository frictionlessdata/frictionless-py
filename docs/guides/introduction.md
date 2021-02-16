---
title: Introduction
---

Frictionless is a framework to describe, extract, validate, and transform tabular data (DEVT Framework). It supports a great deal of data schemes and formats, as well as provides popular platforms integrations. The framework is powered by the lightweight yet comprehensive [Frictionless Data Specifications](https://specs.frictionlessdata.io/).

## Why Frictionless Data?

Generating insight and conclusions from data is often not a straightforward process. Data can be poorly structured, hard to find, archived in difficult to use formats, or incomplete. These issues create “friction” and make it difficult to use, publish and share data. The Frictionless Data project aims to reduce frictions while working with data, with a goal to make it effortless to transport data among different tools and platforms for further analysis. This project is a suite of open source software, tools, and specifications focused on improving data and metadata interoperability. The core software library is [Frictionless-py](https://github.com/frictionlessdata/frictionless-py), and this documentation will help you learn how to use this Frictionless Framework. Are you interested in learning more about the project as a whole? Read this overview section.

## What does the Frictionless Framework do?

The Frictionless Framework helps make data more useable by generating metadata and schemas and validating data to ensure quality. There are four main functions that can be used independently to improve your data: Describe data, Extract data, Validate data, and Transform data (DEVT). Here, we will go into more detail on each of these main functions.

**[D] Describe:** infer and edit a file's metadata. For instance, Describe will generate metadata describing the layout of the data (i.e. which row is the header) and also a schema describing the data contents (i.e. the type of data in a column). This is a first step for ensuring data quality and usability.

**[E] Extract:** read and normalize file's data. By default, extract returns data conforming to the metadata that was either defined in the describe step or inferred automatically. The user can opt-out of this to get the raw (unnormalized) data. Frictionless supports various file schemes like HTTP, FTP, and S3 and data formats like CSV, XLS, JSON, SQL, and others.

**[V] Validate:** detect errors in the file. Validate runs checks on data tables, resources, and datasets to identify potential issues (i.e. are there any missing values?). These checks can be modified and can be based on a provided schema. While extract cleans the data by removing the invalid cells, validate helps to see the whole picture of the raw file.

**[T] Transform:** change the file's metadata and data. This step can including reshaping data, saving it in a different format, or uploading the data somewhere. Frictionless provides a pipeline capability and a lower-level interface to work with the data.

In contrast to an ETL-framework (extract-transform-load), the DEVT-framework does not have a linear flow. For example, let’s look at some user stories:
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

## What is Frictionless Framework based on?

The core of the Framework is the Frictionless Specifications. These specifications are a set of patterns for describing data including Data Package (for datasets), Data Resource (for files) and Table Schema (for tables). A Data Package is a simple container format used to describe and package a collection of data and metadata, including schemas. Frictionless-py lets users create data packages and schemas that conform to the Frictionless specifications.
You can read more about the Frictionless specifications here: https://specs.frictionlessdata.io/.

## Features

- Powerful Python framework
- Convenient command-line interface
- Low memory consumption for data of any size
- Reasonable performance on big data
- Support for compressed files
- Custom checks and formats
- Fully pluggable architecture
- An included API server
- Open source
- More than 1000+ tests

## Example

```bash title="CLI"
frictionless validate data/invalid.csv
```
```
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
