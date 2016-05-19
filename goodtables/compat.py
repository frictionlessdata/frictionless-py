# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import tempfile
import io
import csv
import re
from itertools import islice
from goodtables import exceptions

_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)
is_py33 = (is_py3 and _ver[1] == 3)
is_py34 = (is_py3 and _ver[1] == 4)
is_py27 = (is_py2 and _ver[1] == 7)


if is_py2:
    from urlparse import urlparse, urlsplit, urlunsplit
    from urllib import quote, quote_plus
    from urllib2 import urlopen, HTTPError
    from httplib import responses
    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)

    def csv_reader(data, dialect=csv.excel, header_index=0, **kwargs):
        """Read text stream (unicode on Py2.7) as CSV."""

        first_lines = list(islice(data, header_index, header_index + 2))
        dialect = detect_dialect(first_lines)
        
        while not re.findall('[^\w ]', dialect.delimiter): 
            first_lines.append(data.readline())
            dialect = detect_dialect(first_lines)
            
        def iterenc_utf8(data):
            for line in data:
                yield line.encode('utf-8')

        data.seek(0)
        iter = data
        iter = iterenc_utf8(iter)
        csv.field_size_limit(20000000)
        try:
            reader = csv.reader(iter, dialect=dialect, **kwargs)
            for row in reader:
                yield [str(cell, 'utf-8') for cell in row]
        except TypeError as e:
            raise exceptions.DataSourceMalformatedError(msg=e.args[0], file_format='csv')
    
                
        
    def detect_dialect(sample):
        """Detect delimiter and quote chars"""

        try:
            dialect = csv.Sniffer().sniff(''.join(sample))
            dialect.delimiter = dialect.delimiter.encode('utf-8')
            dialect.quotechar = dialect.quotechar.encode('utf-8')
            return dialect
        except csv.Error:
            return csv.excel


elif is_py3:
    from urllib.parse import urlparse, urlsplit, urlunsplit, quote, quote_plus
    from urllib.request import urlopen
    from urllib.error import HTTPError
    from http.client import responses
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)

    def csv_reader(data, header_index, **kwargs):

        def line_iterator(data):
            for line in data:
                yield line

        first_lines = list(islice(data, header_index, header_index + 2))
        dialect = detect_dialect(first_lines)

        while not re.findall('[^\w ]', dialect.delimiter): 
            first_lines.append(data.readline())
            dialect = detect_dialect(first_lines)

        data.seek(0)
        iter = line_iterator(data)
        csv.field_size_limit(20000000)
        try:
            return csv.reader(iter, dialect, **kwargs)
        except TypeError as e:
            raise exceptions.DataSourceMalformatedError(msg=e.args[0], file_format='csv')
        
    def detect_dialect(sample):
        """Detect delimiter and quote chars"""

        try:
            dialect = csv.Sniffer().sniff(''.join(sample))
            return dialect
        except csv.Error:
            return csv.excel


def to_bytes(textstring):
    """Convert a text string to a byte string"""
    return textstring.encode('utf-8')


def to_builtin_str(textstring):
    """Convert textstring to the built-in `str` on the runtime."""

    if is_py2:
        return str.encode('utf-8')
    else:
        return str


def NamedTemporaryFile(mode='w+t', encoding='utf-8', **kwargs):
    """Return a NamedTemporaryFile for the appropriate runtime."""

    if is_py2:
        return tempfile.NamedTemporaryFile(mode=mode, **kwargs)

    elif is_py3:
        return tempfile.NamedTemporaryFile(mode=mode, encoding=encoding,
                                           **kwargs)
