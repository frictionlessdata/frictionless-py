import re
import os
import inspect
import pkgutil
import tempfile
import stringcase
import subprocess
from jinja2 import Template
from docstring_parser import parse
from importlib import import_module
from frictionless import plugins, errors, checks, steps, types, helpers


# Main


def main():
    build_plugins_reference()
    build_schemes_reference()
    build_formats_reference()
    build_errors_reference()
    build_checks_reference()
    build_steps_reference()
    build_types_reference()
    build_api_reference()
    build_contributing()
    build_changelog()
    build_authors()


# References


def build_plugins_reference():
    TEMPLATE = """
    ---
    title: Plugins Reference
    ---

    Frictionless Framework ships with a great deal of core plugins.
    Some of them are production ready and some of them are not.
    - **Stable**: These plugins are well-tested and can be used in production
    - **Experimental**: These plugins are not recommended for production yet. There can be bugs and the API might change within the same major version of Frictionless

    {% for Plugin in Plugins %}
    ## {{ Plugin.__name__ }}

    Code: `{{ Plugin.code }}` <br/>
    Status: `{{ Plugin.status }}` <br/>

    {% endfor %}
    """

    # Input
    Plugins = []
    for item in pkgutil.iter_modules([os.path.dirname(plugins.__file__)]):
        module = import_module(f"frictionless.plugins.{item.name}")
        for name, Plugin in vars(module).items():
            match = re.match(r"(.+)Plugin", name)
            if not match:
                continue
            Plugins.append(Plugin)

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(Plugins=Plugins).strip()
    write_file(os.path.join("docs", "references", "plugins-reference.md"), document)
    print("Built: Plugins Reference")


def build_schemes_reference():
    TEMPLATE = """
    ---
    title: Schemes Reference
    ---

    It's a schemes reference supported by the main Frictionless package. If you have installed external plugins, there can be more schemes available. Below we're listing a scheme group name (or a loader name) like Remote, which is used, for example, for `http`, `https` etc schemes. Options can be used for creating controls, for example, `control = RemoteControl(http_timeout=1)`.

    {% for scheme in schemes %}
    ## {{ scheme.name }}

    {% if scheme.options %}
    {% for option in scheme.options %}
    ### {{ option.name }}

    > Type: {{ option.type }}

    {{ option.text }}
    {% endfor %}
    {% else %}
    There are no options available.
    {% endif %}
    {% endfor %}
    """

    # Input
    schemes = []
    modules = []
    for item in pkgutil.iter_modules([os.path.dirname(plugins.__file__)]):
        modules.append(import_module(f"frictionless.plugins.{item.name}"))
    for module in modules:
        for name, Control in vars(module).items():
            match = re.match(r"(.+)Control", name)
            if not match:
                continue
            name = match.group(1)
            data = parse(Control.__doc__)
            scheme = {"name": name, "options": []}
            for param in data.params:
                if param.arg_name.startswith("descriptor"):
                    continue
                type = param.type_name
                text = param.description.capitalize()
                name = stringcase.titlecase(param.arg_name.replace("?", ""))
                scheme["options"].append({"name": name, "text": text, "type": type})
            schemes.append(scheme)

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(schemes=schemes).strip()
    write_file(os.path.join("docs", "references", "schemes-reference.md"), document)
    print("Built: Schemes Reference")


def build_formats_reference():
    TEMPLATE = """
    ---
    title: Formats Reference
    ---

    It's a formats reference supported by the main Frictionless package. If you have installed external plugins, there can be more formats available. Below we're listing a format group name (or a parser name) like Excel, which is used, for example, for `xlsx`, `xls` etc formats. Options can be used for creating dialects, for example, `dialect = ExcelDialect(sheet=1)`.

    {% for format in formats %}
    ## {{ format.name }}

    {% if format.options %}
    {% for option in format.options %}
    ### {{ option.name }}

    > Type: {{ option.type }}

    {{ option.text }}
    {% endfor %}
    {% else %}
    There are no options available.
    {% endif %}
    {% endfor %}
    """

    # Input
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

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(formats=formats).strip()
    write_file(os.path.join("docs", "references", "formats-reference.md"), document)
    print("Built: Formats Reference")


def build_errors_reference():
    TEMPLATE = """
    ---
    title: Errors Reference
    ---

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

    # Input
    Errors = [item for item in vars(errors).values() if hasattr(item, "code")]

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(Errors=Errors).strip()
    write_file(os.path.join("docs", "references", "errors-reference.md"), document)
    print("Built: Errors Reference")


def build_checks_reference():
    TEMPLATE = """
    ---
    title: Checks Reference
    ---

    This document provides a full reference to the Frictionless checks.
    {% for Check in Checks %}
    ## {{ Check.__name__ }}

    Code: `{{ Check.code }}` <br/>

    {% endfor %}
    """

    # Input
    Checks = [item for item in vars(checks).values() if hasattr(item, "code")]

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(Checks=Checks).strip()
    write_file(os.path.join("docs", "references", "checks-reference.md"), document)
    print("Built: Checks Reference")


def build_steps_reference():
    TEMPLATE = """
    ---
    title: Steps Reference
    ---

    This document provides a full reference to the Frictionless steps.
    {% for Step in Steps %}
    ## {{ Step.__name__ }}

    Code: `{{ Step.code }}` <br/>

    {% endfor %}
    """

    # Input
    Steps = [item for item in vars(steps).values() if hasattr(item, "code")]

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(Steps=Steps).strip()
    write_file(os.path.join("docs", "references", "steps-reference.md"), document)
    print("Built: Steps Reference")


def build_types_reference():
    TEMPLATE = """
    ---
    title: Types Reference
    ---

    This document provides a full reference to the Frictionless types.
    {% for Type in Types %}
    ## {{ Type.__name__ }}

    Code: `{{ Type.code }}` <br/>

    {% endfor %}
    """

    # Input
    Types = [item for item in vars(types).values() if hasattr(item, "code")]

    # Output
    template = Template(inspect.cleandoc(TEMPLATE))
    document = template.render(Types=Types).strip()
    write_file(os.path.join("docs", "references", "types-reference.md"), document)
    print("Built: Types Reference")


def build_api_reference():

    # Input
    blocks = {}
    element = None
    command = "pydoc-markdown -p frictionless"
    content = subprocess.check_output(command, shell=True).decode()
    for line in content.splitlines(keepends=True):
        if line.startswith("<a"):
            continue
        if line.startswith("# "):
            element = None
            continue
        if line.startswith("## "):
            element = re.search(r"^## (.*) Objects$", line).group(1)
            continue
        if line.startswith("#### "):
            if not element or element.islower():
                element = re.search(r"^#### (.*)$", line).group(1)
                continue
            prefix = element[0].lower() + element[1:]
            line = re.sub(r"^#### (.*)$", f"### {prefix}.\\1", line)
        if element:
            blocks.setdefault(element, "")
            blocks[element] += line

    # Output
    document = ""
    document += "---\n"
    document += "title: API Reference\n"
    document += "---\n\n"
    for element in sorted(blocks):
        if element.startswith("program"):
            continue
        document += f"## {element}\n"
        document += blocks[element]
    write_file(os.path.join("docs", "references", "api-reference.md"), document)
    print("Built: API Reference")


# Development


def build_contributing():
    document = read_file("CONTRIBUTING.md")
    document = re.sub(r"^# (.*)", "---\ntitle: \\1\n---", document)
    write_file(os.path.join("docs", "development", "contributing.md"), document)
    print("Built: Contributing")


def build_changelog():
    document = read_file("CHANGELOG.md")
    document = re.sub(r"^# (.*)", "---\ntitle: \\1\n---", document)
    write_file(os.path.join("docs", "development", "changelog.md"), document)
    print("Built: Changelog")


def build_migration():
    document = read_file("MIGRATION.md")
    document = re.sub(r"^# (.*)", "---\ntitle: \\1\n---", document)
    write_file(os.path.join("docs", "development", "migraion.md"), document)
    print("Built: Migration")


def build_authors():
    document = read_file("AUTHORS.md")
    document = re.sub(r"^# (.*)", "---\ntitle: \\1\n---", document)
    write_file(os.path.join("docs", "development", "authors.md"), document)
    print("Built: Authors")


# Helpers


def read_file(path):
    with open(path, encoding="utf-8") as file:
        return file.read()


def write_file(path, text):
    with tempfile.NamedTemporaryFile("wt", delete=False, encoding="utf-8") as file:
        file.write(text)
    helpers.move_file(file.name, path)


# System

if __name__ == "__main__":
    main()
