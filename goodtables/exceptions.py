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

    def __init__(self, msg=None):
        self.msg = msg or 'The data source is on a URL that returns an HTTP Error.'


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
