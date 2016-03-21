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
        self.msg = msg or 'The data source is on a URL that returns an HTTP Error.'
        self.status = status
        
    def as_result(self, name=''):
        return {
            'id': 'http_{0}'.format(self.status),
            'name': name if name else self.msg,
            'msg': self.msg,
            'help': '',
            'help_edit': ''
        }


class DataSourceIsHTMLError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'The data source appears to be an HTML document.'


class DataSourceDecodeError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or ('The data source cannot be decoded using the '
                           'declared or detected encoding.')


class InvalidHandlerError(Exception):

    def __init__(self, msg=None):
        self.msg = msg or 'The passed handler is not valid.'
