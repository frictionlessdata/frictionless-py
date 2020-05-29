import io
import json
import requests
import jsonschema
from urllib.parse import urlparse
from . import exceptions
from . import config


# TODO: fix metadata deepcopy behaviour
class Metadata(dict):
    def __init__(
        self, descriptor=None, *, root=None, strict=False, profile=None, Error=None
    ):
        self.__root = root or self
        self.__strict = strict
        self.__profile = profile
        self.__Error = Error
        self.__errors = []
        metadata = self.retrieve_metadata(descriptor)
        dict.update(self, metadata)
        if self and not root:
            self.normalize_metadata()
            self.validate_metadata()

    @property
    def metadata_errors(self):
        return self.__errors

    # Retrieve

    def retrieve_metadata(self, descriptor):
        try:
            if descriptor is None:
                return {}
            if isinstance(descriptor, dict):
                # TODO: deepcopy
                return descriptor
            if isinstance(descriptor, str):
                if urlparse(descriptor).scheme in config.REMOTE_SCHEMES:
                    return requests.get(descriptor).json()
                with io.open(descriptor, encoding='utf-8') as file:
                    return json.load(file)
            return json.load(descriptor)
        except Exception:
            details = 'canot retrieve metadata "%s"' % descriptor
            if not self.__Error or self.__strict:
                raise exceptions.GoodtablesException(details)
            error = self.__Error(details=details)
            self.__errors.append(error)

    # Normalize

    def normalize_metadata(self):
        for key, value in self.items():
            if isinstance(value, dict):
                if not isinstance(value, Metadata):
                    value = Metadata(value, root=self.__root, strict=self.__strict)
                    dict.__setitem__(self, key, value)
                value.normalize_metadata()
            if isinstance(value, list):
                if not isinstance(value, MetadataList):
                    value = MetadataList(value, root=self.__root, strict=self.__strict)
                    dict.__setitem__(self, key, value)
                value.normalize_metadata()

    # Validate

    def validate_metadata(self):
        self.__errors.clear()
        if self.__profile:
            validator_class = jsonschema.validators.validator_for(self.__profile)
            validator = validator_class(self.__profile)
            for error in validator.iter_errors(self):
                message = str(error.message)
                metadata_path = '/'.join(map(str, error.path))
                profile_path = '/'.join(map(str, error.schema_path))
                details = '"%s" at "%s" in metadata and at "%s" in profile'
                details = details % (message, metadata_path, profile_path)
                if not self.__Error or self.__strict:
                    raise exceptions.GoodtablesException(details)
                error = self.__Error(details=details)
                self.__errors.append(error)
        for key, value in self.items():
            if isinstance(value, (Metadata, MetadataList)):
                value.validate_metadata()
                self.__errors.extend(value.metadata_errors)

    # Listeners

    def on_metadata_change(self):
        if self.__root is not self:
            return self.__root.on_metadata_change()
        self.normalize_metadata()
        self.validate_metadata()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.on_metadata_change()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.on_metadata_change()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.on_metadata_change()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.on_metadata_change()
        return result

    def popitem(self, *args, **kwargs):
        result = super().popitem(*args, **kwargs)
        self.on_metadata_change()
        return result

    def setdefault(self, *args, **kwargs):
        result = super().setdefault(*args, **kwargs)
        self.on_metadata_change()
        return result

    def update(self, *args, **kwargs):
        result = super().update(*args, **kwargs)
        self.on_metadata_change()
        return result


class MetadataList(list):
    def __init__(self, values, *, root, strict=False):
        list.extend(self, values)
        self.__root = root
        self.__strict = strict
        self.__errors = []

    @property
    def metadata_errors(self):
        return self.__errors

    # Normalize

    def normalize_metadata(self):
        for index, value in list(enumerate(self)):
            if isinstance(value, dict):
                if not isinstance(value, Metadata):
                    value = Metadata(value, root=self.__root, strict=self.__strict)
                    list.__setitem__(self, index, value)
                value.normalize_metadata()
            if isinstance(value, list):
                if not isinstance(value, MetadataList):
                    value = MetadataList(value, root=self.__root, strict=self.__strict)
                    list.__setitem__(self, index, value)
                value.normalize_metadata()

    # Validate

    def validate_metadata(self):
        for value in self:
            if isinstance(value, (Metadata, MetadataList)):
                value.validate_metadata()
                self.__errors.extend(value.metadata_errors)

    # Listeners

    def on_metadata_change(self):
        self.__root.on_metadata_change()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.on_metadata_change()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.on_metadata_change()
        return result

    def append(self, *args, **kwargs):
        result = super().append(*args, **kwargs)
        self.on_metadata_change()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.on_metadata_change()
        return result

    def extend(self, *args, **kwargs):
        result = super().extend(*args, **kwargs)
        self.on_metadata_change()
        return result

    def insert(self, *args, **kwargs):
        result = super().insert(*args, **kwargs)
        self.on_metadata_change()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.on_metadata_change()
        return result

    def remove(self, *args, **kwargs):
        result = super().remove(*args, **kwargs)
        self.on_metadata_change()
        return result
