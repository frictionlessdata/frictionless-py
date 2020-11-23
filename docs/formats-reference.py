import re
import os
import pkgutil
import stringcase
from scripts import docs
from jinja2 import Template
from docstring_parser import parse
from importlib import import_module
from frictionless import plugins


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


source = os.path.join(docs.SOURCE_DIR, "formats-reference.md")
target_dir = os.path.join(docs.TARGET_DIR, "formats-reference")
target_md = os.path.join(target_dir, "README.md")
os.makedirs(target_dir, exist_ok=True)
formats = get_formats()
with open(source) as file:
    template = Template(file.read())
    document = template.render(formats=formats)
with open(target_md, "wt") as file:
    file.write(document)
