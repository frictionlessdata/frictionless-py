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

    def __init__(self, msg=None, status=None):
        self.msg = 'The data source server responded with an error: {0}'.format(msg)
        self.status = status
        self.name = '{0} error'.format(msg).title()

        
class DataSourceFormatUnsupportedError(Exception):

    def __init__(self, msg=None, file_format=None):
        self.file_format = file_format or 'unsupported'
        self.msg = msg or 'The data source format is {0}.'.format(self.file_format.upper())
        self.name = 'Data Source {0} Error'.format(self.file_format)


class DataSourceDecodeError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or ('The data source cannot be decoded using the '
                           'declared or detected encoding.')
                           
        self.name = 'Data Source Decode Error'


class InvalidHandlerError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'The passed handler is not valid.'
