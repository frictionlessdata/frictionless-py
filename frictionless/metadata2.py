from __future__ import annotations
import io
import re
import json
import yaml
import jsonschema
from pathlib import Path
from collections.abc import Mapping
from importlib import import_module
from typing import TYPE_CHECKING, List
from .exception import FrictionlessException
from . import helpers

if TYPE_CHECKING:
    from .interfaces import IDescriptor, IPlainDescriptor


class Metadata2:

    # Convert

    convert_properties: List[str] = []

    @classmethod
    def from_descriptor(cls, descriptor: IDescriptor):
        descriptor = cls.metadata_extract(descriptor)
        return cls(**{name: descriptor.get(name) for name in cls.convert_properties})  # type: ignore

    def to_descriptor(self) -> IPlainDescriptor:
        return helpers.remove_non_values(
            {name: getattr(self, name) for name in self.convert_properties}
        )

    # Metadata

    metadata_Error = None
    metadata_profile = None

    @property
    def metadata_valid(self):
        """
        Returns:
            bool: whether the metadata is valid
        """
        return not len(self.metadata_errors)

    @property
    def metadata_errors(self):
        """
        Returns:
            Errors[]: a list of the metadata errors
        """
        return list(self.metadata_validate())

    def metadata_validate(self):
        """Validate metadata"""
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
    def metadata_extract(cls, descriptor: IDescriptor) -> Mapping:
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
            note = f'cannot extract metadata "{descriptor}" because "{exception}"'
            raise FrictionlessException(Error(note=note)) from exception
