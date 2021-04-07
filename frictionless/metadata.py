import io
import json
import yaml
import requests
import jsonschema
import stringcase
from pathlib import Path
from operator import setitem
from functools import partial
from importlib import import_module
from .exception import FrictionlessException
from .helpers import cached_property
from . import helpers


# NOTE:
# In general, it will be better to simplify magic used in Metadata
# For exmple, we can make default values (like empty list) immutable
# to get rid of metadata_attach and related complexity
# Also, take a look at `resource.open` all these seitems trigger onchage (innefective)
# We might consider having something like `with metadata.disable_onchange`


class Metadata(helpers.ControlledDict):
    """Metadata representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Metadata`

    Parameters:
        descriptor? (str|dict): metadata descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    metadata_Error = None
    metadata_profile = None
    metadata_duplicate = False

    def __init__(self, descriptor=None):
        self.__Error = self.metadata_Error or import_module("frictionless.errors").Error
        metadata = self.metadata_extract(descriptor)
        for key, value in metadata.items():
            dict.setdefault(self, key, value)
        self.__onchange__()

    def __setattr__(self, name, value):
        if hasattr(self, "_Metadata__Error"):
            for Type in type(self).__mro__:
                if Type is Metadata:
                    break
                attr = Type.__dict__.get(name)
                if attr:
                    write = getattr(attr, "metadata_write", None)
                    if write:
                        if callable(write):
                            return write(self, value)
                        return setitem(self, stringcase.camelcase(name), value)
        if not name.startswith("_"):
            message = f"'{type(self).__name__}' object has no attribute '{name}'"
            raise AttributeError(message)
        return super().__setattr__(name, value)

    def __onchange__(self, onchange=None):
        super().__onchange__(onchange)
        if hasattr(self, "_Metadata__Error"):
            for key, attr in type(self).__dict__.items():
                reset = getattr(attr, "metadata_reset", None)
                if reset and key in self.__dict__:
                    self.__dict__.pop(key)
            self.metadata_process()

    def setinitial(self, key, value):
        """Set an initial item in a subclass' constructor

        Parameters:
            key (str): key
            value (any): value
        """
        if value is not None:
            dict.__setitem__(self, key, value)

    # Expand

    def expand(self):
        pass

    # Infer

    def infer(self):
        pass

    # Import/Export

    def to_copy(self):
        """Create a copy of the metadata

        Returns:
            Metadata: a copy of the metadata
        """
        return type(self)(self.to_dict())

    def to_dict(self):
        """Convert metadata to a plain dict

        Returns:
            dict: metadata as a plain dict
        """
        return helpers.deepfork(self)

    def to_json(self, path=None, encoder_class=None):
        """Save metadata as a json

        Parameters:
            path (str): target path

        Raises:
            FrictionlessException: on any error
        """
        text = json.dumps(self.to_dict(), indent=2, ensure_ascii=False, cls=encoder_class)
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(self.__Error(note=str(exc))) from exc
        return text

    def to_yaml(self, path=None):
        """Save metadata as a yaml

        Parameters:
            path (str): target path

        Raises:
            FrictionlessException: on any error
        """
        text = yaml.dump(self.to_dict(), Dumper=IndentDumper)
        if path:
            try:
                helpers.write_file(path, text)
            except Exception as exc:
                raise FrictionlessException(self.__Error(note=str(exc))) from exc
        return text

    # Metadata

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

    def metadata_attach(self, name, value):
        """Helper method for attaching a value to  the metadata

        Parameters:
            name (str): name
            value (any): value
        """
        if self.get(name) is not value:
            onchange = partial(metadata_attach, self, name)
            if isinstance(value, dict):
                if not isinstance(value, Metadata):
                    value = helpers.ControlledDict(value)
                value.__onchange__(onchange)
            elif isinstance(value, list):
                value = helpers.ControlledList(value)
                value.__onchange__(onchange)
        return value

    def metadata_extract(self, descriptor):
        """Helper method called during the metadata extraction

        Parameters:
            descriptor (any): descriptor
        """
        try:
            if descriptor is None:
                return {}
            if isinstance(descriptor, dict):
                if not self.metadata_duplicate:
                    return descriptor
                try:
                    return helpers.deepfork(descriptor)
                except Exception:
                    note = "descriptor is not serializable"
                    errors = import_module("frictionless.errors")
                    raise FrictionlessException(errors.GeneralError(note=note))
            if isinstance(descriptor, (str, Path)):
                if isinstance(descriptor, Path):
                    descriptor = str(descriptor)
                if helpers.is_remote_path(descriptor):
                    response = requests.get(descriptor)
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
            note = f'cannot extract metadata "{descriptor}" because "{exception}"'
            raise FrictionlessException(self.__Error(note=note)) from exception

    def metadata_process(self):
        """Helper method called on any metadata change"""
        pass

    def metadata_validate(self, profile=None):
        """Helper method called on any metadata change

        Parameters:
            profile (dict): a profile to validate against of
        """
        profile = profile or self.metadata_profile
        if profile:
            validator_class = jsonschema.validators.validator_for(profile)
            validator = validator_class(profile)
            for error in validator.iter_errors(self):
                # Withouth this resource with both path/data is invalid
                if "is valid under each of" in error.message:
                    continue
                metadata_path = "/".join(map(str, error.path))
                profile_path = "/".join(map(str, error.schema_path))
                note = '"%s" at "%s" in metadata and at "%s" in profile'
                note = note % (error.message, metadata_path, profile_path)
                yield self.__Error(note=note)
        yield from []

    # Helpers

    @staticmethod
    def property(func=None, *, cache=True, reset=True, write=True):
        """Create a metadata property

        Parameters:
            func (func): method
            cache? (bool): cache
            reset? (bool): reset
            write? (func): write
        """

        # Not caching
        if not cache:
            return property

        # Actual property
        def metadata_property(func):
            prop = cached_property(func)
            setattr(prop, "metadata_reset", reset)
            setattr(prop, "metadata_write", write)
            return prop

        # Allow both forms
        return metadata_property(func) if func else metadata_property


# Internal


def metadata_attach(self, name, value):
    # Using standalone `setitem` without a wrapper doesn't work for Python3.6
    return setitem(self, name, value)


class IndentDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)
