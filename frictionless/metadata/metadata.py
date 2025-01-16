from __future__ import annotations

import inspect
import io
import json
import pprint
import re
from collections.abc import Mapping
from copy import deepcopy
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    Generator,
    List,
    Optional,
    Set,
    Type,
    Union,
)

from typing_extensions import Self

from .. import helpers
from ..exception import FrictionlessException
from ..platform import platform
from ..vendors import stringcase  # type: ignore

if TYPE_CHECKING:
    from .. import types
    from ..error import Error
    from ..report import Report


class Metadata:
    """Metadata representation

    For proper functioning a child class must be decorated by
    "@attrs.define(kw_only=True, repr=False)" and ensure that
    "Metadata.__attrs_post_init__" is called

    """

    custom: dict[str, Any] = {}
    """
    List of custom parameters. Any extra properties will be added
    to the custom property.
    """

    def __new__(cls, *args: Any, **kwargs: Any):
        obj = super().__new__(cls)
        obj.custom = obj.custom.copy()
        obj.metadata_defaults = cls.metadata_defaults.copy()
        obj.metadata_assigned = cls.metadata_assigned.copy()
        obj.metadata_assigned.update(kwargs.keys())
        return obj

    def __attrs_post_init__(self):
        self.metadata_initiated = True

    def __setattr__(self, name: str, value: Any):
        if not name.startswith(("_", "metadata_")):
            if self.metadata_initiated:
                if value is not None:
                    self.metadata_assigned.add(name)
                elif name in self.metadata_assigned:
                    self.metadata_assigned.remove(name)
            elif isinstance(value, (list, dict)):
                self.metadata_defaults[name] = value.copy()  # type: ignore
            elif isinstance(value, type):
                self.metadata_defaults[name] = value.__dict__.copy()  # type: ignore
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        return pprint.pformat(self.to_descriptor(), sort_dicts=False)

    @property
    def description_html(self) -> str:
        """Description in HTML"""
        description = getattr(self, "description", "")
        try:
            html = platform.marko.convert(description)
            html = html.replace("\n", "")
            return html
        except Exception:
            return ""

    @property
    def description_text(self) -> str:
        """Description in Text"""

        class HTMLFilter(platform.html_parser.HTMLParser):
            text = ""

            def handle_data(self, data: str):
                self.text += data
                self.text += " "

        parser = HTMLFilter()
        parser.feed(self.description_html)
        return parser.text.strip()

    # Defined

    def list_defined(self) -> List[str]:
        defined = list(self.metadata_assigned)
        for name, default in self.metadata_defaults.items():
            value = getattr(self, name, None)
            if isinstance(value, type):
                value = value.__dict__.copy()  # type: ignore
            if value != default:
                defined.append(name)
        return defined

    def add_defined(self, name: str) -> None:
        self.metadata_assigned.add(name)

    def has_defined(self, name: str) -> bool:
        return name in self.list_defined()

    def get_defined(self, name: str, *, default: Any = None) -> Any:
        if self.has_defined(name):
            return getattr(self, name)
        if default is not None:
            return default

    def set_not_defined(self, name: str, value: Any, *, distinct: bool = False) -> None:
        if not self.has_defined(name) and value is not None:
            if distinct and getattr(self, name, None) == value:
                return
            setattr(self, name, value)

    # Validate

    @classmethod
    def validate_descriptor(
        cls, descriptor: Union[types.IDescriptor, str], *, basepath: Optional[str] = None
    ) -> Report:
        errors = []
        timer = helpers.Timer()
        try:
            cls.from_descriptor(descriptor, basepath=basepath)
        except FrictionlessException as exception:
            errors = exception.reasons if exception.reasons else [exception.error]
        return platform.frictionless.Report.from_validation(
            time=timer.time, errors=errors
        )

    # Convert

    # TODO: remove
    @classmethod
    def from_options(cls, *args: Any, **options: Any) -> Self:
        return cls(*args, **helpers.remove_non_values(options))

    @classmethod
    def from_descriptor(
        cls,
        descriptor: Union[types.IDescriptor, str],
        allow_invalid: bool = False,
        **options: Any,
    ) -> Self:
        descriptor_path = None
        if isinstance(descriptor, str):
            descriptor_path = descriptor
            basepath = options.pop("basepath", None)
            descriptor = helpers.join_basepath(descriptor, basepath)
            if "basepath" in inspect.signature(cls.__init__).parameters:
                options["basepath"] = helpers.parse_basepath(descriptor)
        descriptor = cls.metadata_retrieve(descriptor)
        # TODO: remove in next version
        # Transform with a base class in case the type is not available
        cls.metadata_transform(descriptor)
        type = descriptor.get("type")
        class_type = vars(cls).get("type")
        if isinstance(class_type, str):
            type = class_type
        Class = cls.metadata_select_class(type)
        Error = Class.metadata_Error or platform.frictionless_errors.MetadataError
        Class.metadata_transform(descriptor)
        errors = list(Class.metadata_validate(descriptor))
        if not allow_invalid:
            if errors:
                error = Error(note="descriptor is not valid")
                raise FrictionlessException(error, reasons=errors)
        metadata = Class.metadata_import(descriptor, **helpers.remove_non_values(options))
        if descriptor_path:
            metadata.metadata_descriptor_path = descriptor_path
            metadata.metadata_descriptor_initial = metadata.to_descriptor()
        return metadata  # type: ignore

    def to_descriptor(self, *, validate: bool = False) -> types.IDescriptor:
        descriptor = self.metadata_export()
        if validate:
            Error = self.metadata_Error or platform.frictionless_errors.MetadataError
            errors = list(self.metadata_validate(descriptor))
            if errors:
                error = Error(note="descriptor is not valid")
                raise FrictionlessException(error, reasons=errors)
        return descriptor

    def to_descriptor_source(self) -> Union[types.IDescriptor, str]:
        """Export metadata as a descriptor or a descriptor path"""
        descriptor = self.to_descriptor()
        if self.metadata_descriptor_path:
            if self.metadata_descriptor_initial == descriptor:
                return self.metadata_descriptor_path
        return descriptor

    def to_copy(self, **options: Any) -> Self:
        """Create a copy of the metadata"""
        return type(self).from_descriptor(self.to_descriptor(), **options)

    def to_dict(self) -> types.IDescriptor:
        """Export metadata as dictionary (alias for "to_descriptor")"""
        return self.to_descriptor()

    def to_json(
        self, path: Optional[str] = None, encoder_class: Optional[Any] = None
    ) -> str:
        """Save metadata as a json

        Parameters:
            path (str): target path
        """
        Error = self.metadata_Error or platform.frictionless_errors.MetadataError
        text = helpers.to_json(self.to_descriptor(), encoder_class=encoder_class)
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(Error(note=str(exc))) from exc
        return text

    def to_yaml(self, path: Optional[str] = None) -> str:
        """Save metadata as a yaml

        Parameters:
            path (str): target path
        """
        Error = self.metadata_Error or platform.frictionless_errors.MetadataError
        text = helpers.to_yaml(self.to_descriptor())
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(Error(note=str(exc))) from exc
        return text

    def to_markdown(self, path: Optional[str] = None, table: bool = False) -> str:
        """Convert metadata as a markdown

        This feature has been contributed to the framework by Ethan Welty (@ezwelty):
        - https://github.com/frictionlessdata/frictionless-py/issues/837

        Parameters:
            path (str): target path
            table (bool): if true converts markdown to tabular format
        """
        Error = self.metadata_Error or platform.frictionless_errors.MetadataError
        mapper = platform.frictionless_formats.markdown.MarkdownMapper()
        text = mapper.write_metadata(self, table=table)  # type: ignore
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(Error(note=str(exc))) from exc
        return text

    # Metadata

    metadata_type: ClassVar[str]
    metadata_Error: ClassVar[Optional[Type[Error]]] = None
    metadata_profile: ClassVar[Dict[str, Any]] = {}
    metadata_profile_patch: ClassVar[Dict[str, Any]] = {}
    metadata_profile_merged: ClassVar[Dict[str, Any]] = {}
    metadata_initiated: bool = False
    metadata_assigned: Set[str] = set()
    metadata_defaults: Dict[str, Any] = {}
    metadata_descriptor_path: Optional[str] = None
    metadata_descriptor_initial: Optional[types.IDescriptor] = None

    @classmethod
    def metadata_select_class(cls, type: Optional[str]) -> Type[Metadata]:
        if type:
            note = f'unsupported type for "{cls.metadata_type}": {type}'
            Error = cls.metadata_Error or platform.frictionless_errors.MetadataError
            raise FrictionlessException(Error(note=note))
        return cls

    @classmethod
    def metadata_select_property_class(cls, name: str) -> Optional[Type[Metadata]]:
        pass

    @classmethod
    def metadata_ensure_profile(cls):
        if not cls.__dict__.get("metadata_profile_merged", None):
            cls.metadata_profile_merged = cls.metadata_profile
            for subcls in reversed(cls.mro()):
                cls.metadata_profile_merged = helpers.merge_jsonschema(
                    cls.metadata_profile_merged,
                    getattr(subcls, "metadata_profile_patch", {}),
                )
        return cls.metadata_profile_merged

    @classmethod
    def metadata_retrieve(
        cls, descriptor: Union[types.IDescriptor, str], *, size: Optional[int] = None
    ) -> types.IDescriptor:
        try:
            if isinstance(descriptor, Mapping):
                return deepcopy(descriptor)
            if isinstance(descriptor, (str, Path)):  # type: ignore
                if isinstance(descriptor, Path):
                    descriptor = str(descriptor)
                if helpers.is_remote_path(descriptor):
                    session = platform.frictionless.system.http_session
                    response = session.get(descriptor, stream=True)
                    response.raise_for_status()
                    response.raw.decode_content = True
                    content = response.raw.read(size).decode("utf-8")
                    response.close()
                else:
                    with open(descriptor, encoding="utf-8") as file:
                        content = file.read(size)
                if descriptor.endswith(".yaml"):
                    metadata = platform.yaml.safe_load(io.StringIO(content))
                else:
                    metadata = json.loads(content)
                assert isinstance(metadata, dict)
                return metadata  # type: ignore
            raise TypeError("descriptor type is not supported")
        except Exception as exception:
            Error = cls.metadata_Error or platform.frictionless_errors.MetadataError
            note = f'cannot retrieve metadata "{descriptor}" because "{exception}"'
            raise FrictionlessException(Error(note=note)) from exception

    @classmethod
    def metadata_transform(cls, descriptor: types.IDescriptor):
        profile = cls.metadata_ensure_profile()
        for name in profile.get("properties", {}):
            value = descriptor.get(name)
            Class = cls.metadata_select_property_class(name)
            if Class:
                if isinstance(value, list):
                    for item in value:  # type: ignore
                        if isinstance(item, dict):
                            type = item.get("type")  # type: ignore
                            ItemClass = Class.metadata_select_class(type)  # type: ignore
                            ItemClass.metadata_transform(item)  # type: ignore
                elif isinstance(value, dict):
                    Class.metadata_transform(value)  # type: ignore

    @classmethod
    def metadata_validate(
        cls,
        descriptor: types.IDescriptor,
        *,
        profile: Optional[Union[types.IDescriptor, str]] = None,
        error_class: Optional[Type[Error]] = None,
    ) -> Generator[Error, None, None]:
        Error = error_class
        if not Error:
            Error = cls.metadata_Error or platform.frictionless_errors.MetadataError
        profile = profile or cls.metadata_ensure_profile()
        if isinstance(profile, str):
            profile = cls.metadata_retrieve(profile)
        validator_class = platform.jsonschema.validators.validator_for(profile)  # type: ignore
        validator = validator_class(profile)  # type: ignore
        for error in validator.iter_errors(descriptor):  # type: ignore
            metadata_path = "/".join(map(str, error.path))  # type: ignore
            message = re.sub(r"\s+", " ", error.message)  # type: ignore
            note = message
            if metadata_path:
                note = f"{note} at property '{metadata_path}'"
            yield Error(note=note)
        for name in profile.get("properties", {}):
            value = descriptor.get(name)
            Class = cls.metadata_select_property_class(name)
            if Class:
                if isinstance(value, list):
                    for item in value:  # type: ignore
                        if isinstance(item, dict):
                            type = item.get("type")  # type: ignore
                            ItemClass = Class.metadata_select_class(type)  # type: ignore
                            yield from ItemClass.metadata_validate(item)  # type: ignore
                elif isinstance(value, dict):
                    yield from Class.metadata_validate(value)  # type: ignore

    @classmethod
    def metadata_import(
        cls, descriptor: types.IDescriptor, *, with_basepath: bool = False, **options: Any
    ) -> Self:
        merged_options = {}
        profile = cls.metadata_ensure_profile()
        basepath = options.pop("basepath", None)
        is_typed_class = isinstance(getattr(cls, "type", None), str)
        for name in profile.get("properties", {}):
            value = descriptor.pop(name, None)
            if value is None or value == {}:
                continue
            if name == "type" and is_typed_class:
                continue
            Class = cls.metadata_select_property_class(name)
            if Class:
                if isinstance(value, list):
                    for ix, item in enumerate(value):  # type: ignore
                        if isinstance(item, dict):
                            type = item.get("type")  # type: ignore
                            ItemClass = Class.metadata_select_class(type)  # type: ignore
                            value[ix] = ItemClass.metadata_import(item, basepath=basepath)  # type: ignore
                        elif isinstance(item, str):
                            value[ix] = Class.from_descriptor(item, basepath=basepath)
                elif isinstance(value, dict):
                    value = Class.metadata_import(value, basepath=basepath)  # type: ignore
            merged_options.setdefault(stringcase.snakecase(name), value)  # type: ignore
        merged_options.update(options)  # type: ignore
        if with_basepath:
            merged_options["basepath"] = basepath
        metadata = cls(**merged_options)
        metadata.custom = descriptor
        return metadata

    def metadata_export(self, *, exclude: List[str] = []) -> types.IDescriptor:
        descriptor = {}
        profile = self.metadata_ensure_profile()
        for name in profile.get("properties", {}):
            if name in exclude:
                continue
            if name != "type" and not self.has_defined(stringcase.snakecase(name)):  # type: ignore
                continue
            value = getattr(self, stringcase.snakecase(name), None)  # type: ignore
            Class = self.metadata_select_property_class(name)
            if value is None or (isinstance(value, dict) and value == {}):
                continue
            if Class:
                if isinstance(value, list):
                    value = [item.to_descriptor_source() for item in value]  # type: ignore
                else:
                    value = value.to_descriptor_source()  # type: ignore
                    if not value:
                        continue
            if isinstance(value, (list, dict)):
                value = deepcopy(value)  # type: ignore
            descriptor[name] = value
        descriptor.update(self.custom)  # type: ignore
        return descriptor  # type: ignore
