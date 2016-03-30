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
    
    STATUS_NAMES = { 404: 'Not Found', 403: 'Forbidden', 401: 'Unauthorized',
                     500: 'Internal Server Error', 503: 'Server Unavailable'}

    def __init__(self, msg=None, status=None):
        self.msg = msg or 'The data source is on a URL that returns an HTTP Error.'
        self.status = status
        
    def as_result(self, name=''):
        return {
            'id': 'http_{0}'.format(self.status),
            'name': name or self.STATUS_NAMES.get(self.status, self.msg),
            'msg': self.msg,
            'help': '',
            'help_edit': ''
        }

        
class DataSourceFormatUnsupportedError(Exception):

    def __init__(self, msg=None, file_format=None):
        self.file_format = file_format or 'unsupported'
        self.msg = msg or 'The data source format is {0}.'.format(self.file_format.upper())
            
            
    def as_result(self, name=''):
        return {
            'id': 'data_{0}_error'.format(self.file_format),
            'name': name or self.msg,
            'msg': self.msg,
            'help': '',
            'help_edit': ''
        }   
        


class DataSourceDecodeError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or ('The data source cannot be decoded using the '
                           'declared or detected encoding.')
                           
    def as_result(self, name=''):
        return {
            'id': 'data_decode_error',
            'name': name or 'Unable to decode data source',
            'msg': self.msg,
            'help': '',
            'help_edit': ''
        } 


class InvalidHandlerError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'The passed handler is not valid.'
