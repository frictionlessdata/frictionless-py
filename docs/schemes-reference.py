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
# Schemes Reference

It's a schemes reference supported by the main Frictionless package. If you have installed external plugins, there can be more schemes available. Below we're listing a scheme group name (or a loader name) like Remote, which is used, for example, for `http`, `https` etc schemes. Options can be used for creating controls, for example, `control = RemoteControl(http_timeout=1)`.

{% for scheme in schemes %}
## {{ scheme.name }}

{% if scheme.options %}
### Options
{% for option in scheme.options %}
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


def get_schemes():
    schemes = []
    modules = []
    for item in pkgutil.iter_modules([os.path.dirname(plugins.__file__)]):
        modules.append(import_module(f"frictionless.plugins.{item.name}"))
    for module in modules:
        for name, Dialect in vars(module).items():
            match = re.match(r"(.+)Control", name)
            if not match:
                continue
            name = match.group(1)
            data = parse(Dialect.__doc__)
            scheme = {"name": name, "options": []}
            for param in data.params:
                if param.arg_name.startswith("descriptor"):
                    continue
                type = param.type_name
                text = param.description.capitalize()
                name = stringcase.titlecase(param.arg_name.replace("?", ""))
                scheme["options"].append({"name": name, "text": text, "type": type})
            schemes.append(scheme)
    return schemes


# Main


schemes = get_schemes()
template = Template(TEMPLATE)
document = template.render(schemes=schemes).strip()
sys.stdout.write(document)
