import io
import json
import requests
import jsonschema
from copy import deepcopy
from urllib.parse import urlparse
from . import exceptions
from . import config


class Descriptor(dict):
    def __init__(self, descriptor=None, *, root=None, strict=False, **props):
        descriptor = self.retrieve_descriptor(descriptor)
        dict.update(self, descriptor)
        dict.update(self, props)
        self.__root = root or self
        self.__strict = strict
        self.__errors = []
        if not root:
            self.normalize_descriptor()
            self.validate_descriptor()

    @property
    def root(self):
        return self.__root

    @property
    def strict(self):
        return self.__strict

    @property
    def errors(self):
        return self.__errors

    @property
    def profile(self):
        return None

    @property
    def Error(self):
        return None

    # Retrieve

    @staticmethod
    def retrieve_descriptor(descriptor):
        try:
            if descriptor is None:
                return {}
            if isinstance(descriptor, dict):
                return deepcopy(descriptor)
            if isinstance(descriptor, str):
                if urlparse(descriptor).scheme in config.REMOTE_SCHEMES:
                    return requests.get(descriptor).json()
                with io.open(descriptor, encoding='utf-8') as file:
                    return json.load(file)
            return json.load(descriptor)
        except Exception:
            raise exceptions.GoodtablesException('Cannot load descriptor')

    # Normalize

    def normalize_descriptor(self):
        for key, value in self.items():
            if isinstance(value, dict):
                if not isinstance(value, Descriptor):
                    value = Descriptor(value, root=self.root, strict=self.strict)
                    dict.__setitem__(self, key, value)
                value.normalize_descriptor()
            if isinstance(value, list):
                if not isinstance(value, DescriptorList):
                    value = DescriptorList(value, root=self.root, strict=self.strict)
                    dict.__setitem__(self, key, value)
                value.normalize_descriptor()

    # Validate

    def validate_descriptor(self):
        self.__errors = []
        if self.profile:
            validator = jsonschema.validators.validator_for(self.profile)(self.profile)
            for error in validator.iter_errors(self):
                message = str(error.message)
                descriptor_path = '/'.join(map(str, error.path))
                profile_path = '/'.join(map(str, error.schema_path))
                details = '%s at "%s" in descriptor and at "%s" in profile'
                details = details % (message, descriptor_path, profile_path)
                if not self.Error or self.strict:
                    raise exceptions.GoodtablesException(details)
                error = self.Error(details=details)
                self.__errors.append(error)
        for key, value in self.items():
            if isinstance(value, (Descriptor, DescriptorList)):
                value.validate_descriptor()
                self.__errors.extend(value.errors)

    # Listeners

    def on_descriptor_change(self):
        if self.root is not self:
            return self.root.on_descriptor_change()
        self.normalize_descriptor()
        self.validate_descriptor()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def popitem(self, *args, **kwargs):
        result = super().popitem(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def setdefault(self, *args, **kwargs):
        result = super().setdefault(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def update(self, *args, **kwargs):
        result = super().update(*args, **kwargs)
        self.on_descriptor_change()
        return result


class DescriptorList(list):
    def __init__(self, descriptors, *, root, strict=False):
        list.extend(self, descriptors)
        self.__root = root
        self.__strict = strict
        self.__errors = []

    @property
    def root(self):
        return self.__root

    @property
    def strict(self):
        return self.__strict

    @property
    def errors(self):
        return self.__errors

    # Normalize

    def normalize_descriptor(self):
        for index, descriptor in list(enumerate(self)):
            if not isinstance(descriptor, Descriptor):
                descriptor = Descriptor(descriptor, root=self.root, strict=self.strict)
                list.__setitem__(self, index, descriptor)
            descriptor.normalize_descriptor()

    # Validate

    def validate_descriptor(self):
        for descriptor in self:
            descriptor.validate_descriptor()
            self.__errors.extend(descriptor.errors)

    # Listeners

    def on_descriptor_change(self):
        self.root.on_descriptor_change()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def append(self, *args, **kwargs):
        result = super().append(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def extend(self, *args, **kwargs):
        result = super().extend(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def insert(self, *args, **kwargs):
        result = super().insert(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.on_descriptor_change()
        return result

    def remove(self, *args, **kwargs):
        result = super().remove(*args, **kwargs)
        self.on_descriptor_change()
        return result
