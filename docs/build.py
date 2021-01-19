import re
import os
import sys
import pkgutil
import stringcase
import subprocess
from jinja2 import Template
from subprocess import check_output
from docstring_parser import parse
from importlib import import_module
from frictionless import plugins, errors


# API Reference

content = check_output("pydoc-markdown -p frictionless", shell=True).decode()
for line in content.splitlines(keepends=True):
    line = re.sub(r"^## ", "### ", line)
    line = re.sub(r"^# ", "## ", line)
    line = re.sub(r"^## frictionless$", "# API Reference", line)
    line = re.sub(r" Objects$", "", line)
    line = re.sub(r"^#### (.*)$", "#### <big>\\1</big>", line)
    sys.stdout.write(line)


# Schemes Reference

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


schemes = get_schemes()
template = Template(TEMPLATE)
document = template.render(schemes=schemes).strip()
sys.stdout.write(document)


# Formats Reference


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


formats = get_formats()
template = Template(TEMPLATE)
document = template.render(formats=formats).strip()
sys.stdout.write(document)


# Error Reference


TEMPLATE = """
# Errors Reference

> This work is based on [Data Quality Spec](https://github.com/frictionlessdata/data-quality-spec)

This document provides a full reference to the Frictionless errors.
{% for Error in Errors %}
## {{ Error.name }}

Code: `{{ Error.code }}` <br/>
Tags: `{{ Error.tags|join(' ') or '-' }}` <br/>
Template: `{{ Error.template }}` <br/>
Description: `{{ Error.description }}` <br/>

{% endfor %}
"""


template = Template(TEMPLATE)
Errors = [item for item in vars(errors).values() if hasattr(item, "code")]
document = template.render(Errors=Errors).strip()
sys.stdout.write(document)


# General


SOURCE_DIR = os.path.join("docs")
TARGET_DIR = os.path.join("docs", "build")


# Main


def main(name=None):
    for path in sorted(os.listdir(SOURCE_DIR)):
        filename = os.path.splitext(path)[0]
        if name and name != filename:
            continue
        fullpath = os.path.join(SOURCE_DIR, path)
        if os.path.isfile(fullpath):
            if path.endswith(".py"):
                from_python(filename)
            elif path.endswith(".md"):
                from_markdown(filename)
            print(f"Built: {filename}")


# Converters


def from_python(name):
    source_py = os.path.join(SOURCE_DIR, f"{name}.py")
    target_dir = os.path.join(TARGET_DIR, name)
    target_md = os.path.join(target_dir, "README.md")
    command = f"python3 {source_py}"
    content = subprocess.check_output(command, shell=True)
    os.makedirs(target_dir, exist_ok=True)
    with open(target_md, "wb") as file:
        file.write(content)


def from_markdown(name):
    source_md = os.path.join(SOURCE_DIR, f"{name}.md")
    target_dir = os.path.join(TARGET_DIR, name)
    target_md = os.path.join(target_dir, "README.md")
    target_py = os.path.join(target_dir, "README.ipynb")
    os.makedirs(target_dir, exist_ok=True)
    command = f"notedown {source_md} --run > {target_py} --match python"
    subprocess.run(command, shell=True, check=True)
    command = f"python3 -m nbconvert {target_py} --to markdown --log-level 0"
    subprocess.run(command, shell=True, check=True)
    lines = []
    with open(target_md) as file:
        for index, line in enumerate(file.read().splitlines()):
            line = line.replace("[0m", "")
            line = line.replace("[1m", "")
            line = line.rstrip()
            if "README_files" in line:
                line = line.replace("README_files", "./README_files")
            lines.append(line)
    with open(target_md, "w") as file:
        file.write("\n".join(lines))


# Main

if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else None
    main(name=name)
