# Extension Guide

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1yj_1Nk8RwMTV2QZ-0RR_cbKN6aQQ5jAb)



Frictionless is built on top of a powerful plugins system which is used internally and allows to extend the framework.



## Plugin Interface

Here is a list of available hooks that you can implement in your plugin:
- `create_check`
- `create_control`
- `create_dialect`
- `create_loader`
- `create_parser`
- `create_server`

To create a plugin you need:
- create a module called `frictionless_<name>` available in PYTHONPATH
- subclass the Plugin class and override one of the methods above

Please consult with "API Reference" for in-detail information about the Plugin interface and how these methods can be implemented.



## Plugin Example

Let's say we're interested in supporting the `csv2k` format that we have just invented. For simplicity, let's use a format that is exactly the same with CSV.

First of all, we need to create a `frictionless_csv2k` module containing a Plugin implementation and a Parser implementation but we're going to re-use the CsvParser as our new format is the same:

> frictionless_csv2k.py

```python
from frictionless import Plugin, parsers

class Csv2kPlugin(Plugin):
    def create_parser(self, file):
        if file.format == "csv2k":
            return Csv2kParser(file)

class Csv2kParser(parsers.CsvParser):
    pass
```

Now, we can just use our new format in any of Frctionless functions that accept a table source, for example, `extract` or `Table`:

```python
from frictionless import extract

rows = extract('data/table.csv2k')
print(rows)
```

This example is over-simplified to show the high-level mechanics but actually writing Frctionless Plugins is really easy. For inspiration, you can checks the `frictionless/plugins` directory and learn from real-life examples. Also, in the Frictionless codebase there are many `Check`, `Control`, `Dialect`, `Loader`, `Parser`, and `Server` implementations - you can read their code for better understanding of how to write your own subclass.
