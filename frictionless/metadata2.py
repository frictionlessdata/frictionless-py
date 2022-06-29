from __future__ import annotations
import os
import io
import re
import json
import yaml
import jinja2
import pprint
import jsonschema
import stringcase
from pathlib import Path
from collections.abc import Mapping
from importlib import import_module
from typing import TYPE_CHECKING, Iterator, Optional, Union, List, Dict, Any, Set
from .exception import FrictionlessException
from . import helpers

if TYPE_CHECKING:
    from .interfaces import IDescriptor, IPlainDescriptor
    from .error import Error


# NOTE: review and clean this class
# NOTE: can we generate metadata_profile from dataclasses?
# NOTE: insert __init__ params docs using instance properties data?


class Metaclass(type):
    def __call__(cls, *args, **kwargs):
        obj = type.__call__(cls, *args, **kwargs)
        obj.metadata_assigned.update(kwargs.keys())
        obj.metadata_initiated = True
        return obj


class Metadata2(metaclass=Metaclass):
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.metadata_assigned = cls.metadata_assigned.copy()
        obj.metadata_defaults = cls.metadata_defaults.copy()
        return obj

    def __setattr__(self, name, value):
        if self.metadata_initiated:
            self.metadata_assigned.add(name)
        elif isinstance(value, (list, dict)):
            if not name.startswith("metadata_"):
                self.metadata_defaults[name] = value.copy()
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return pprint.pformat(self.to_descriptor())

    # Properties

    def list_defined(self):
        defined = list(self.metadata_assigned)
        for name, default in self.metadata_defaults.items():
            if getattr(self, name, None) != default:
                defined.append(name)
        return defined

    def has_defined(self, name: str):
        return name in self.list_defined()

    def get_defined(self, name: str, *, default=None):
        if self.has_defined(name):
            return getattr(self, name)
        if default is not None:
            return default

    def set_not_defined(self, name: str, value):
        if not self.has_defined(name) and value is not None:
            setattr(self, name, value)

    # Validate

    def validate(self):
        timer = helpers.Timer()
        errors = self.metadata_errors
        Report = import_module("frictionless").Report
        return Report.from_validation(time=timer.time, errors=errors)

    # Convert

    @classmethod
    def from_descriptor(cls, descriptor: IDescriptor):
        """Import metadata from a descriptor"""
        return cls.metadata_import(descriptor)

    def to_descriptor(self) -> IPlainDescriptor:
        """Export metadata as a plain descriptor"""
        return self.metadata_export()

    # TODO: review
    def to_copy(self):
        """Create a copy of the metadata"""
        return type(self).from_descriptor(self.metadata_export())

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to a plain dict"""
        return self.metadata_export()

    def to_json(self, path=None, encoder_class=None):
        """Save metadata as a json

        Parameters:
            path (str): target path
        """
        frictionless = import_module("frictionless")
        Error = self.metadata_Error or frictionless.errors.MetadataError
        text = json.dumps(self.to_dict(), indent=2, ensure_ascii=False, cls=encoder_class)
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(Error(note=str(exc))) from exc
        return text

    def to_yaml(self, path=None):
        """Save metadata as a yaml

        Parameters:
            path (str): target path
        """
        frictionless = import_module("frictionless")
        Error = self.metadata_Error or frictionless.errors.MetadataError
        text = yaml.dump(
            self.to_dict(),
            sort_keys=False,
            allow_unicode=True,
            Dumper=IndentDumper,
        )
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(Error(note=str(exc))) from exc
        return text

    def to_markdown(self, path: Optional[str] = None, table: bool = False) -> str:
        """Convert metadata as a markdown

        This feature has been contributed to the framwork by Ethan Welty (@ezwelty):
        - https://github.com/frictionlessdata/frictionless-py/issues/837

        Parameters:
            path (str): target path
            table (bool): if true converts markdown to tabular format
        """
        frictionless = import_module("frictionless")
        Error = self.metadata_Error or frictionless.errors.MetadataError
        filename = self.__class__.__name__.lower()
        template = f"{filename}-table.md" if table is True else f"{filename}.md"
        md_output = render_markdown(f"{template}", {filename: self}).strip()
        if path:
            try:
                helpers.write_file(path, md_output)
            except Exception as exc:
                raise FrictionlessException(Error(note=str(exc))) from exc
        return md_output

    # Metadata

    # TODO: add/improve types
    metadata_Error = None
    metadata_profile = None
    metadata_assigned: Set[str] = set()
    metadata_defaults: Dict[str, Union[list, dict]] = {}
    metadata_initiated: bool = False

    @property
    def metadata_valid(self) -> bool:
        """Whether metadata is valid"""
        return not len(self.metadata_errors)

    @property
    def metadata_errors(self) -> List[Error]:
        """List of metadata errors"""
        return list(self.metadata_validate())

    @classmethod
    def metadata_properties(cls, **Types):
        """Extract metadata properties"""
        properties = {}
        if cls.metadata_profile:
            for name in cls.metadata_profile.get("properties", []):
                properties[name] = Types.get(name)
        return properties

    # TODO: automate metadata_validate of the children using metadata_properties!!!
    def metadata_validate(self) -> Iterator[Error]:
        """Validate metadata and emit validation errors"""
        if self.metadata_profile:
            frictionless = import_module("frictionless")
            Error = self.metadata_Error or frictionless.errors.MetadataError
            validator_class = jsonschema.validators.validator_for(self.metadata_profile)  # type: ignore
            validator = validator_class(self.metadata_profile)
            for error in validator.iter_errors(self.to_descriptor()):
                # Withouth this resource with both path/data is invalid
                if "is valid under each of" in error.message:
                    continue
                metadata_path = "/".join(map(str, error.path))
                profile_path = "/".join(map(str, error.schema_path))
                # We need it because of the metadata.__repr__ overriding
                message = re.sub(r"\s+", " ", error.message)
                note = '"%s" at "%s" in metadata and at "%s" in profile'
                note = note % (message, metadata_path, profile_path)
                yield Error(note=note)
        yield from []

    @classmethod
    def metadata_import(cls, descriptor: IDescriptor):
        """Import metadata from a descriptor source"""
        target = {}
        source = cls.metadata_normalize(descriptor)
        for name, Type in cls.metadata_properties().items():
            value = source.get(name)
            if value is None:
                continue
            # TODO: rebase on "type" only?
            if name in ["code", "type"]:
                continue
            if Type:
                if isinstance(value, list):
                    value = [Type.from_descriptor(item) for item in value]
                else:
                    value = Type.from_descriptor(value)
            target[stringcase.snakecase(name)] = value
        return cls(**target)  # type: ignore

    def metadata_export(self) -> IPlainDescriptor:
        """Export metadata as a descriptor"""
        descriptor = {}
        for name, Type in self.metadata_properties().items():
            value = getattr(self, stringcase.snakecase(name), None)
            if value is None:
                continue
            # TODO: rebase on "type" only?
            if name not in ["code", "type"]:
                if not self.has_defined(stringcase.snakecase(name)):
                    continue
            if Type:
                if isinstance(value, list):
                    value = [item.metadata_export() for item in value]  # type: ignore
                else:
                    value = value.metadata_export()  # type: ignore
            descriptor[name] = value
        return descriptor

    # TODO: return plain descriptor?
    @classmethod
    def metadata_normalize(cls, descriptor: IDescriptor) -> Mapping:
        """Extract metadata"""
        try:
            if isinstance(descriptor, Mapping):
                return descriptor
            if isinstance(descriptor, (str, Path)):
                if isinstance(descriptor, Path):
                    descriptor = str(descriptor)
                if helpers.is_remote_path(descriptor):
                    system = import_module("frictionless.system").system
                    http_session = system.get_http_session()
                    response = http_session.get(descriptor)
                    response.raise_for_status()
                    content = response.text
                else:
                    with open(descriptor, encoding="utf-8") as file:
                        content = file.read()
                if descriptor.endswith((".yaml", ".yml")):
                    metadata = yaml.safe_load(io.StringIO(content))
                else:
                    metadata = json.loads(content)
                assert isinstance(metadata, dict)
                return metadata
            raise TypeError("descriptor type is not supported")
        except Exception as exception:
            frictionless = import_module("frictionless")
            Error = cls.metadata_Error or frictionless.errors.MetadataError
            note = f'cannot normalize metadata "{descriptor}" because "{exception}"'
            raise FrictionlessException(Error(note=note)) from exception


# Internal


class IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


def render_markdown(path: str, data: dict) -> str:
    """Render any JSON-like object as Markdown, using jinja2 template"""

    template_dir = os.path.join(os.path.dirname(__file__), "assets/templates")
    environ = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir), lstrip_blocks=True, trim_blocks=True
    )
    environ.filters["filter_dict"] = filter_dict
    environ.filters["dict_to_markdown"] = json_to_markdown
    environ.filters["tabulate"] = dicts_to_markdown_table
    template = environ.get_template(path)
    return template.render(**data)


def filter_dict(
    x: dict,
    include: Optional[list] = None,
    exclude: Optional[list] = None,
    order: Optional[list] = None,
) -> dict:
    """Filter and order dictionary by key names"""

    if include:
        x = {key: x[key] for key in x if key in include}
    if exclude:
        x = {key: x[key] for key in x if key not in exclude}
    if order:
        index = [
            (order.index(key) if key in order else len(order), i)
            for i, key in enumerate(x)
        ]
        sorted_keys = [key for _, key in sorted(zip(index, x.keys()))]
        x = {key: x[key] for key in sorted_keys}
    return x


def json_to_markdown(
    x: Union[dict, list, int, float, str, bool],
    level: int = 0,
    tab: int = 2,
    flatten_scalar_lists: bool = True,
) -> str:
    """Render any JSON-like object as Markdown, using nested bulleted lists"""

    def _scalar_list(x) -> bool:
        return isinstance(x, list) and all(not isinstance(xi, (dict, list)) for xi in x)

    def _iter(x: Union[dict, list, int, float, str, bool], level: int = 0) -> str:
        if isinstance(x, (dict, list)):
            if isinstance(x, dict):
                labels = [f"- `{key}`" for key in x]
            elif isinstance(x, list):
                labels = [f"- [{i + 1}]" for i in range(len(x))]
            values = x if isinstance(x, list) else list(x.values())
            if isinstance(x, list) and flatten_scalar_lists:
                scalar = [not isinstance(value, (dict, list)) for value in values]
                if all(scalar):
                    values = [f"{values}"]
            lines = []
            for label, value in zip(labels, values):
                if isinstance(value, (dict, list)) and (
                    not flatten_scalar_lists or not _scalar_list(value)
                ):
                    lines.append(f"{label}\n{_iter(value, level=level + 1)}")
                else:
                    if isinstance(value, str):
                        # Indent to align following lines with '- '
                        value = jinja2.filters.do_indent(value, width=2, first=False)  # type: ignore
                    lines.append(f"{label} {value}")
            txt = "\n".join(lines)
        else:
            txt = str(x)
        if level > 0:
            txt = jinja2.filters.do_indent(txt, width=tab, first=True, blank=False)  # type: ignore
        return txt

    return jinja2.filters.do_indent(  # type: ignore
        _iter(x, level=0), width=tab * level, first=True, blank=False
    )


def dicts_to_markdown_table(dicts: List[dict], **kwargs) -> str:
    """Tabulate dictionaries and render as a Markdown table"""

    if kwargs:
        dicts = [filter_dict(x, **kwargs) for x in dicts]
    try:
        pandas = import_module("pandas")
        df = pandas.DataFrame(dicts)
    except ImportError:
        module = import_module("frictionless.exception")
        raise module.FrictionlessException("Please install `pandas` package")
    return df.where(df.notnull(), None).to_markdown(index=False)
