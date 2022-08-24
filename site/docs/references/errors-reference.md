---
title: Errors Reference
---

> This work is based on [Data Quality Spec](https://github.com/frictionlessdata/data-quality-spec)

This document provides a full reference to the Frictionless errors.

## General Error

Code: `general-error` <br/>
Tags: `-` <br/>
Template: `General error: {note}` <br/>
Description: `There is an error.` <br/>


## Row Error

Code: `row-error` <br/>
Tags: `#table #row` <br/>
Template: `Row Error` <br/>
Description: `Row Error` <br/>


## Cell Error

Code: `cell-error` <br/>
Tags: `#table #row #cell` <br/>
Template: `Cell Error` <br/>
Description: `Cell Error` <br/>


## Extra Cell

Code: `extra-cell` <br/>
Tags: `#table #row #cell` <br/>
Template: `Row at position "{rowPosition}" has an extra value in field at position "{fieldPosition}"` <br/>
Description: `This row has more values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.` <br/>


## Missing Cell

Code: `missing-cell` <br/>
Tags: `#table #row #cell` <br/>
Template: `Row at position "{rowPosition}" has a missing cell in field "{fieldName}" at position "{fieldPosition}"` <br/>
Description: `This row has less values compared to the header row (the first row in the data source). A key concept is that all the rows in tabular data must have the same number of columns.` <br/>


## Type Error

Code: `type-error` <br/>
Tags: `#table #row #cell` <br/>
Template: `Type error in the cell "{cell}" in row "{rowPosition}" and field "{fieldName}" at position "{fieldPosition}": {note}` <br/>
Description: `The value does not match the schema type and format for this field.` <br/>


## Constraint Error

Code: `constraint-error` <br/>
Tags: `#table #row #cell` <br/>
Template: `The cell "{cell}" in row at position "{rowPosition}" and field "{fieldName}" at position "{fieldPosition}" does not conform to a constraint: {note}` <br/>
Description: `A field value does not conform to a constraint.` <br/>


## Unique Error

Code: `unique-error` <br/>
Tags: `#table #row #cell` <br/>
Template: `Row at position "{rowPosition}" has unique constraint violation in field "{fieldName}" at position "{fieldPosition}": {note}` <br/>
Description: `This field is a unique field but it contains a value that has been used in another row.` <br/>


## Truncated Value

Code: `truncated-value` <br/>
Tags: `#table #row #cell` <br/>
Template: `The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}` <br/>
Description: `The value is possible truncated.` <br/>


## Forbidden Value

Code: `forbidden-value` <br/>
Tags: `#table #row #cell` <br/>
Template: `The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}` <br/>
Description: `The value is forbidden.` <br/>


## Sequential Value

Code: `sequential-value` <br/>
Tags: `#table #row #cell` <br/>
Template: `The cell {cell} in row at position {rowPosition} and field {fieldName} at position {fieldPosition} has an error: {note}` <br/>
Description: `The value is not sequential.` <br/>


## Error

Code: `error` <br/>
Tags: `-` <br/>
Template: `{note}` <br/>
Description: `Error` <br/>


## File Error

Code: `file-error` <br/>
Tags: `#file` <br/>
Template: `General file error: {note}` <br/>
Description: `There is a file error.` <br/>


## Hash Count Error

Code: `hash-count-error` <br/>
Tags: `#file` <br/>
Template: `The data source does not match the expected hash count: {note}` <br/>
Description: `This error can happen if the data is corrupted.` <br/>


## Byte Count Error

Code: `byte-count-error` <br/>
Tags: `#file` <br/>
Template: `The data source does not match the expected byte count: {note}` <br/>
Description: `This error can happen if the data is corrupted.` <br/>


## Package Error

Code: `package-error` <br/>
Tags: `-` <br/>
Template: `The data package has an error: {note}` <br/>
Description: `A validation cannot be processed.` <br/>


## Resource Error

Code: `resource-error` <br/>
Tags: `-` <br/>
Template: `The data resource has an error: {note}` <br/>
Description: `A validation cannot be processed.` <br/>


## Pipeline Error

Code: `pipeline-error` <br/>
Tags: `-` <br/>
Template: `Pipeline is not valid: {note}` <br/>
Description: `Provided pipeline is not valid.` <br/>


## Inquiry Error

Code: `inquiry-error` <br/>
Tags: `-` <br/>
Template: `Inquiry is not valid: {note}` <br/>
Description: `Provided inquiry is not valid.` <br/>


## Control Error

Code: `control-error` <br/>
Tags: `-` <br/>
Template: `Control is not valid: {note}` <br/>
Description: `Provided control is not valid.` <br/>


## Dialect Error

Code: `dialect-error` <br/>
Tags: `-` <br/>
Template: `Dialect is not valid: {note}` <br/>
Description: `Provided dialect is not valid.` <br/>


## Layout Error

Code: `layout-error` <br/>
Tags: `-` <br/>
Template: `Layout is not valid: {note}` <br/>
Description: `Provided layout is not valid.` <br/>


## Schema Error

Code: `schema-error` <br/>
Tags: `-` <br/>
Template: `Schema is not valid: {note}` <br/>
Description: `Provided schema is not valid.` <br/>


## Field Error

Code: `field-error` <br/>
Tags: `-` <br/>
Template: `Field is not valid: {note}` <br/>
Description: `Provided field is not valid.` <br/>


## Report Error

Code: `report-error` <br/>
Tags: `-` <br/>
Template: `Report is not valid: {note}` <br/>
Description: `Provided report is not valid.` <br/>


## Status Error

Code: `status-error` <br/>
Tags: `-` <br/>
Template: `Status is not valid: {note}` <br/>
Description: `Provided status is not valid.` <br/>


## Check Error

Code: `check-error` <br/>
Tags: `-` <br/>
Template: `Check is not valid: {note}` <br/>
Description: `Provided check is not valid` <br/>


## Step Error

Code: `step-error` <br/>
Tags: `-` <br/>
Template: `Step is not valid: {note}` <br/>
Description: `Provided step is not valid` <br/>


## Source Error

Code: `source-error` <br/>
Tags: `-` <br/>
Template: `The data source has not supported or has inconsistent contents: {note}` <br/>
Description: `Data reading error because of not supported or inconsistent contents.` <br/>


## Scheme Error

Code: `scheme-error` <br/>
Tags: `-` <br/>
Template: `The data source could not be successfully loaded: {note}` <br/>
Description: `Data reading error because of incorrect scheme.` <br/>


## Format Error

Code: `format-error` <br/>
Tags: `-` <br/>
Template: `The data source could not be successfully parsed: {note}` <br/>
Description: `Data reading error because of incorrect format.` <br/>


## Encoding Error

Code: `encoding-error` <br/>
Tags: `-` <br/>
Template: `The data source could not be successfully decoded: {note}` <br/>
Description: `Data reading error because of an encoding problem.` <br/>


## Hashing Error

Code: `hashing-error` <br/>
Tags: `-` <br/>
Template: `The data source could not be successfully hashed: {note}` <br/>
Description: `Data reading error because of a hashing problem.` <br/>


## Compression Error

Code: `compression-error` <br/>
Tags: `-` <br/>
Template: `The data source could not be successfully decompressed: {note}` <br/>
Description: `Data reading error because of a decompression problem.` <br/>


## Storage Error

Code: `storage-error` <br/>
Tags: `-` <br/>
Template: `The storage has an error: {note}` <br/>
Description: `A storage's operation cannot be performed` <br/>


## Task Error

Code: `task-error` <br/>
Tags: `-` <br/>
Template: `The task has an error: {note}` <br/>
Description: `General task-level error.` <br/>


## Table Error

Code: `table-error` <br/>
Tags: `#table` <br/>
Template: `General table error: {note}` <br/>
Description: `There is a table error.` <br/>


## Header Error

Code: `header-error` <br/>
Tags: `#table #header` <br/>
Template: `Cell Error` <br/>
Description: `Cell Error` <br/>


## Blank Header

Code: `blank-header` <br/>
Tags: `#table #header` <br/>
Template: `Header is completely blank` <br/>
Description: `This header is empty. A header should contain at least one value.` <br/>


## Label Error

Code: `label-error` <br/>
Tags: `#table #header #label` <br/>
Template: `Label Error` <br/>
Description: `Label Error` <br/>


## Extra Label

Code: `extra-label` <br/>
Tags: `#table #header #label` <br/>
Template: `There is an extra label "{label}" in header at position "{fieldPosition}"` <br/>
Description: `The header of the data source contains label that does not exist in the provided schema.` <br/>


## Missing Label

Code: `missing-label` <br/>
Tags: `#table #header #label` <br/>
Template: `There is a missing label in the header's field "{fieldName}" at position "{fieldPosition}"` <br/>
Description: `Based on the schema there should be a label that is missing in the data's header.` <br/>


## Blank Label

Code: `blank-label` <br/>
Tags: `#table #header #label` <br/>
Template: `Label in the header in field at position "{fieldPosition}" is blank` <br/>
Description: `A label in the header row is missing a value. Label should be provided and not be blank.` <br/>


## Duplicate Label

Code: `duplicate-label` <br/>
Tags: `#table #header #label` <br/>
Template: `Label "{label}" in the header at position "{fieldPosition}" is duplicated to a label: {note}` <br/>
Description: `Two columns in the header row have the same value. Column names should be unique.` <br/>


## Incorrect Label

Code: `incorrect-label` <br/>
Tags: `#table #header #label` <br/>
Template: `Label "{label}" in field {fieldName} at position "{fieldPosition}" does not match the field name in the schema` <br/>
Description: `One of the data source header does not match the field name defined in the schema.` <br/>


## Blank Row

Code: `blank-row` <br/>
Tags: `#table #row` <br/>
Template: `Row at position "{rowPosition}" is completely blank` <br/>
Description: `This row is empty. A row should contain at least one value.` <br/>


## PrimaryKey Error

Code: `primary-key-error` <br/>
Tags: `#table #row` <br/>
Template: `Row at position "{rowPosition}" violates the primary key: {note}` <br/>
Description: `Values in the primary key fields should be unique for every row` <br/>


## ForeignKey Error

Code: `foreign-key-error` <br/>
Tags: `#table #row` <br/>
Template: `Row at position "{rowPosition}" violates the foreign key: {note}` <br/>
Description: `Values in the foreign key fields should exist in the reference table` <br/>


## Duplicate Row

Code: `duplicate-row` <br/>
Tags: `#table #row` <br/>
Template: `Row at position {rowPosition} is duplicated: {note}` <br/>
Description: `The row is duplicated.` <br/>


## Row Constraint

Code: `row-constraint` <br/>
Tags: `#table #row` <br/>
Template: `The row at position {rowPosition} has an error: {note}` <br/>
Description: `The value does not conform to the row constraint.` <br/>


## Field Count Error

Code: `field-count-error` <br/>
Tags: `#table` <br/>
Template: `The data source does not match the expected field count: {note}` <br/>
Description: `This error can happen if the data is corrupted.` <br/>


## Row Count Error

Code: `row-count-error` <br/>
Tags: `#table` <br/>
Template: `The data source does not match the expected row count: {note}` <br/>
Description: `This error can happen if the data is corrupted.` <br/>


## Table dimensions error

Code: `table-dimensions-error` <br/>
Tags: `#table` <br/>
Template: `The data source does not have the required dimensions: {note}` <br/>
Description: `This error can happen if the data is corrupted.` <br/>


## Deviated Value

Code: `deviated-value` <br/>
Tags: `#table` <br/>
Template: `There is a possible error because the value is deviated: {note}` <br/>
Description: `The value is deviated.` <br/>