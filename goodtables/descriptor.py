import io
import json
import requests
import jsonschema
from copy import deepcopy
from urllib.parse import urlparse
from . import exceptions
from . import config


class Descriptor(dict):
    def __init__(self, descriptor=None, **props):
        descriptor = self.retrieve(descriptor)
        descriptor.update(props)
        descriptor = self.normalize(descriptor)
        self.__strict = props.pop('strict', False)
        self.__errors = self.validate(
            descriptor, profile=self.profile, Error=self.Error, strict=self.strict,
        )
        self.update(descriptor)

    @property
    def profile(self):
        return None

    @property
    def Error(self):
        return None

    @property
    def strict(self):
        return self.__strict

    @property
    def errors(self):
        return self.__errors

    # Prepare

    @staticmethod
    def retrieve(descriptor):

        try:
            # None
            if descriptor is None:
                return {}

            # Inline
            if isinstance(descriptor, dict):
                return deepcopy(descriptor)

            # String
            if isinstance(descriptor, str):
                if urlparse(descriptor).scheme in config.REMOTE_SCHEMES:
                    return requests.get(descriptor).json()
                with io.open(descriptor, encoding='utf-8') as file:
                    return json.load(file)

            # Stream
            return json.load(descriptor)

        except Exception:
            raise exceptions.GoodtablesException('Cannot load descriptor')

    @staticmethod
    def normalize(descriptor):
        return descriptor

    @staticmethod
    def validate(descriptor, *, profile=None, Error=None, strict=False):
        errors = []
        if profile:
            validator = jsonschema.validators.validator_for(profile)(profile)
            for error in validator.iter_errors(descriptor):
                message = str(error.message)
                descriptor_path = '/'.join(map(str, error.path))
                profile_path = '/'.join(map(str, error.schema_path))
                details = '%s at "%s" in descriptor and at "%s" in profile'
                details = details % (message, descriptor_path, profile_path)
                if not Error or strict:
                    raise exceptions.GoodtablesException(details)
                error = Error(details=details)
                errors.append(error)
        return errors
