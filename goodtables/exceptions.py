# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class InvalidSpec(Exception):
    pass


class PipelineBuildError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'Could not build the pipeline.'


class ProcessorBuildError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'Could not build the processor.'


class DataSourceHTTPError(Exception):

    def __init__(self, msg=None, status=None, name=None):

        from goodtables import compat

        self.status = status
        self.msg = msg or ('The data source server responded with an error: '
                           '{0}.').format(compat.responses.get(self.status, ''))
        self.name = name or '{0} Error'.format(compat.responses.get(self.status, 'http'))

        
class DataSourceFormatUnsupportedError(Exception):

    def __init__(self, msg=None, file_format=None, name=None):
        self.file_format = file_format or 'unsupported'
        self.msg = msg or 'The data source format is {0}.'.format(self.file_format.upper())
        self.name = name or 'Data Source {0} Error'.format(self.file_format)


class DataSourceDecodeError(Exception):

    def __init__(self, msg=None, name=None):
        self.msg = msg or ('The data source cannot be decoded using the '
                           'declared or detected encoding.')
        self.name = name or 'Data Source Decode Error'

    
class DataSourceMalformatedError(Exception):

    def __init__(self, msg=None, file_format=None, name=None):
        self.file_format = file_format or 'tabular file'
        self.msg = 'The data source is an invalid {0}: {1}.'.format(self.file_format, msg)
        self.name = name or 'Invalid {0} Error'.format(self.file_format).title()


class InvalidHandlerError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'The passed handler is not valid.'

class InvalidPipelineOptions(ValueError):

    def __init__(self, msg=None):
        self.msg = msg or 'Some of the options are not valid.'
