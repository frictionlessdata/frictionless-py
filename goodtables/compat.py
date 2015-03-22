# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import sys
import tempfile
import io
import csv


_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)
is_py33 = (is_py3 and _ver[1] == 3)
is_py34 = (is_py3 and _ver[1] == 4)
is_py27 = (is_py2 and _ver[1] == 7)


if is_py2:
    import urlparse as parse
    from urllib2 import urlopen, HTTPError
    builtin_str = str
    bytes = str
    str = unicode
    basestring = basestring
    numeric_types = (int, long, float)

    def csv_reader(data, dialect=csv.excel, **kwargs):
        """Read text stream (unicode on Py2.7) as CSV."""

        def iterenc_utf8(data):
            for line in data:
                yield line.encode('utf-8')

        reader = csv.reader(iterenc_utf8(data), dialect=dialect, **kwargs)
        for row in reader:
            yield [str(cell, 'utf-8') for cell in row]


elif is_py3:
    from urllib import parse
    from urllib.request import urlopen
    from urllib.error import HTTPError
    csv_reader = csv.reader
    builtin_str = str
    str = str
    bytes = bytes
    basestring = (str, bytes)
    numeric_types = (int, float)


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
