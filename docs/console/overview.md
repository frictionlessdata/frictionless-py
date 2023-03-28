# Overview

The Command-Line interface is a vital part for the Frictionless Framework. While working within Python provides more flexibility, CLI is the easist way to interact with Frictionless.

```yaml video/youtube
code: 7a_rL9j-gn8
```

## Install

To install the package please follow the [Getting Started](../getting-started.html) guide. Usually, a simple installation using Pip or Anaconda will install the `frictionless` binary on your computer so you don't need to install CLI aditionally.

## Commands

The `frictionless` binary requires providing a command like `describe` or `validate`:

```bash tabs=CLI
frictionless describe # to describe your data
frictionless explore # to explore your data
frictionless extract # to extract your data
frictionless index # to index your data
frictionless list # to list your data
frictionless publish # to publish your data
frictionless query # to query your data
frictionless script # to script your data
frictionless validate # to validate your data
frictionless --help # to get list of the command
frictionless --version # to get the version
```

## Arguments

All the arguments for the main CLI command are the same as they are in Python. You can read [Guides](../guides/describing-data.html) and use almost all the information from there within the command-line. There is an important different in how arguments are written (note the dashes):

```
Python: validate('data/table.csv', limit_errors=1)
CLI: $ validate data/table.csv --limit-errors 1
```

To get help for a command and its arguments you can use the help flag with the command:

```bash tabs=CLI
frictionless describe --help # to get help for describe
frictionless extract --help # to get help for extract
frictionless validate --help # to get help for validate
frictionless transform --help # to get help for transform
```

## Outputs

Usually, Frictionless commands returns pretty-formatted tabular data like `extract` or `validate` do. For the `describe` command you get a metadata back and you can choose in what format to return it:

```bash tabs=CLI
frictionless describe # default YAML with a commented front-matter
frictionless describe --yaml # standard YAML
frictionless describe --json # standard JSON
```

## Errors

The Frictionless' CLI interface should not fail with any internal Python errors with a traceback (a long listing of related code). If you see something like this please create an issue in the [Issue Tracker](https://github.com/frictionlessdata/frictionless-py/issues).

## Debug

To debug a problem please use:

```bash tabs=CLI
frictionless command --debug
```
