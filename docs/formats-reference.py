import re
import os
import sys
import pkgutil
import stringcase
from jinja2 import Template
from docstring_parser import parse
from importlib import import_module
from frictionless import plugins


TEMPLATE = """
# Formats Reference

It's a formats reference supported by the main Frictionless package. If you have installed external plugins, there can be more formats available. Below we're listing a format group name (or a parser name) like Excel, which is used, for example, for `xlsx`, `xls` etc formats. Options can be used for creating dialects, for example, `dialect = ExcelDialect(sheet=1)`.

{% for format in formats %}
## {{ format.name }}

{% if format.options %}
### Options
{% for option in format.options %}
#### {{ option.name }}

> Type: {{ option.type }}

{{ option.text }}
{% endfor %}
{% else %}
There are no options available.
{% endif %}
{% endfor %}
"""


# Helpers


def get_formats():
    formats = []
    modules = []
    for item in pkgutil.iter_modules([os.path.dirname(plugins.__file__)]):
        modules.append(import_module(f"frictionless.plugins.{item.name}"))
    for module in modules:
        for name, Dialect in vars(module).items():
            match = re.match(r"(.+)Dialect", name)
            if not match:
                continue
            name = match.group(1)
            data = parse(Dialect.__doc__)
            format = {"name": name, "options": []}
            for param in data.params:
                if param.arg_name.startswith("descriptor"):
                    continue
                type = param.type_name
                text = param.description.capitalize()
                name = stringcase.titlecase(param.arg_name.replace("?", ""))
                format["options"].append({"name": name, "text": text, "type": type})
            formats.append(format)
    return formats


# Main


formats = get_formats()
template = Template(TEMPLATE)
document = template.render(formats=formats).strip()
sys.stdout.write(document)
