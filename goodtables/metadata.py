import io
import json
import requests
import jsonschema
from copy import deepcopy
from urllib.parse import urlparse
from cached_property import cached_property
from . import exceptions
from . import config


class Metadata(dict):
    metadata_Error = None
    metadata_profile = None

    def __init__(self, descriptor=None, *, root=None, strict=False):
        self.__root = root or self
        self.__strict = strict or not self.metadata_Error
        self.__errors = []
        metadata = self.extract_metadata(descriptor)
        dict.update(self, metadata)
        if self and not root:
            self.process_metadata()
            self.validate_metadata()

    @cached_property
    def metadata_root(self):
        return self.__root

    @cached_property
    def metadata_strict(self):
        return self.__strict

    @property
    def metadata_valid(self):
        return not len(self.__errors)

    @cached_property
    def metadata_errors(self):
        return self.__errors

    # Duplicate

    def duplicate_metadata(self):
        result = {}
        for key, value in self.items():
            if hasattr(value, 'duplicate_metadata'):
                value = value.copy()
            result[key] = value
        return result

    def copy(self):
        return self.duplicate_metadata()

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()

    # Extract

    def extract_metadata(self, descriptor):
        try:
            if descriptor is None:
                return {}
            if isinstance(descriptor, dict):
                return descriptor
            if isinstance(descriptor, str):
                if urlparse(descriptor).scheme in config.REMOTE_SCHEMES:
                    return requests.get(descriptor).json()
                with io.open(descriptor, encoding='utf-8') as file:
                    return json.load(file)
            return json.load(descriptor)
        except Exception:
            details = 'canot retrieve metadata "%s"' % descriptor
            if self.metadata_strict:
                raise exceptions.GoodtablesException(details)
            error = self.metadata_Error(details=details)
            self.metadata_errors.append(error)

    # Process

    def process_metadata(self):
        pass

    # Validate

    def validate_metadata(self):
        self.metadata_errors.clear()
        if self.metadata_profile:
            validator_class = jsonschema.validators.validator_for(self.metadata_profile)
            validator = validator_class(self.metadata_profile)
            for error in validator.iter_errors(self):
                message = str(error.message)
                metadata_path = '/'.join(map(str, error.path))
                profile_path = '/'.join(map(str, error.schema_path))
                details = '"%s" at "%s" in metadata and at "%s" in profile'
                details = details % (message, metadata_path, profile_path)
                if self.metadata_strict:
                    raise exceptions.GoodtablesException(details)
                error = self.metadata_Error(details=details)
                self.metadata_errors.append(error)


class ControlledMetadata(Metadata):

    # Extract

    def extract_metadata(self, descriptor):
        if isinstance(descriptor, dict):
            return deepcopy(descriptor)
        super().extract_metadata(descriptor)

    # Process

    def process_metadata(self):
        for key, value in self.items():
            if isinstance(value, dict):
                if not hasattr(value, 'on_metadata_transform'):
                    value = ControlledMetadata(
                        value, root=self.metadata_root, strict=self.metadata_strict
                    )
                    dict.__setitem__(self, key, value)
                value.process_metadata()
            if isinstance(value, list):
                if not hasattr(value, 'on_metadata_transform'):
                    value = ControlledMetadataList(
                        value, root=self.metadata_root, strict=self.metadata_strict
                    )
                    dict.__setitem__(self, key, value)
                value.process_metadata()

    # Transform

    def on_metadata_transform(self):
        if self.metadata_root is not self:
            return self.metadata_root.on_metadata_transform()
        self.process_metadata()
        self.validate_metadata()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def popitem(self, *args, **kwargs):
        result = super().popitem(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def setdefault(self, *args, **kwargs):
        result = super().setdefault(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def update(self, *args, **kwargs):
        result = super().update(*args, **kwargs)
        self.on_metadata_transform()
        return result

    # Validate

    def validate_metadata(self):
        super().validate_metadata()
        for key, value in self.items():
            if hasattr(value, 'validate_metadata'):
                value.validate_metadata()
                self.metadata_errors.extend(value.metadata_errors)


class ControlledMetadataList(list):
    def __init__(self, values, *, root, strict=False):
        list.extend(self, values)
        self.__root = root
        self.__strict = strict
        self.__errors = []

    @cached_property
    def metadata_root(self):
        return self.__root

    @cached_property
    def metadata_strict(self):
        return self.__strict

    @cached_property
    def metadata_errors(self):
        return self.__errors

    # Duplicate

    def duplicate_metadata(self):
        result = []
        for value in self:
            if hasattr(value, 'duplicate_metadata'):
                value = value.copy()
            result.append(value)
        return result

    def copy(self):
        return self.duplicate_metadata()

    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()

    # Process

    def process_metadata(self):
        for index, value in list(enumerate(self)):
            if isinstance(value, dict):
                if not hasattr(value, 'on_metadata_transform'):
                    value = ControlledMetadata(
                        value, root=self.metadata_root, strict=self.metadata_strict
                    )
                    list.__setitem__(self, index, value)
                value.process_metadata()
            if isinstance(value, list):
                if not hasattr(value, 'on_metadata_transform'):
                    value = ControlledMetadataList(
                        value, root=self.metadata_root, strict=self.metadata_strict
                    )
                    list.__setitem__(self, index, value)
                value.process_metadata()

    # Transform

    def on_metadata_transform(self):
        self.metadata_root.on_metadata_transform()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def append(self, *args, **kwargs):
        result = super().append(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def extend(self, *args, **kwargs):
        result = super().extend(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def insert(self, *args, **kwargs):
        result = super().insert(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.on_metadata_transform()
        return result

    def remove(self, *args, **kwargs):
        result = super().remove(*args, **kwargs)
        self.on_metadata_transform()
        return result

    # Validate

    def validate_metadata(self):
        for value in self:
            if hasattr(value, 'validate_metadata'):
                value.validate_metadata()
                self.metadata_errors.extend(value.metadata_errors)
