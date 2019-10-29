# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

import json
from datapackage import Package
from ...registry import check
from ...error import Error
from ... import exceptions


# Module API

@check('file-integrity', type='custom', context='body')
class FileIntegrity(object):

    # Public

    def __init__(self, **options):
        self.__size = None
        self.__hash = None
        self.__stream = None

    def prepare(self, stream, schema, extra):
        descriptor = extra['datapackage']
        if descriptor.strip().startswith('{'):
            descriptor = json.loads(descriptor)
        resource = Package(descriptor).get_resource(extra['resource-name'])
        self.__size = resource.descriptor.get('bytes', None)
        self.__hash = _extract_sha256_hash(resource.descriptor.get('hash', None))
        self.__stream = stream
        return True

    def check_row(self, cells):
        pass

    def check_table(self):
        errors = []

        # Check size
        if self.__size and self.__size != self.__stream.size:
            message = 'File size doesn\'t match provided value'
            errors.append(Error('file-integrity', message=message))

        # Check hash
        if self.__hash and self.__hash != self.__stream.hash:
            message = 'File hash doesn\'t match provided value'
            errors.append(Error('file-integrity', message=message))

        return errors


# Internal

def _extract_sha256_hash(hash):
    prefix = 'sha256:'
    if hash and hash.startswith(prefix):
        return hash.replace(prefix, '')
    return None
