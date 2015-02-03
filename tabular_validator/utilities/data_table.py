# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
from .. import compat


class DataTable(object):

    """Convert a data source into a formatted (csv, json) utf-8 text stream."""

    REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')

    def __init__(self, data_source, headers=None, filepath=None):

        self.openfiles = []
        self.filepath = filepath
        self.stream = self.to_textstream(data_source)
        self.headers, self.values = self.extract(headers)

    def extract(self, headers=None):
        """Extract headers and values from the data stream."""
        if compat.is_py2:
            quote_char = compat.str("'")
        else:
            quote_char = "'"

        headers = headers or self.get_headers(self.stream.readline())
        values = compat.csv.reader(self.stream, quotechar=quotechar)

        return headers, values

    def to_dict(self):
        raise NotImplementedError

    def to_csv(self, filepath=None):
        raise NotImplementedError

    def to_json(self, filepath=None):
        raise NotImplementedError

    def to_textstream(self, data_source):

        """Return a text stream from data_source.

        Args:
            data_source: An interface to data.
                Can be a stream, a string, a file path, or a URL path.

        Returns:
            A utf-8 encoded text stream.

        """

        if isinstance(data_source, io.IOBase):
            if isinstance(data_source, io.TextIOBase):
                return data_source
            else:
                return io.TextIOWrapper(data_source)

        elif compat.parse.urlparse(data_source).scheme in self.REMOTE_SCHEMES:
            return io.TextIOWrapper(compat.urlopen(data_source),
                                    encoding='utf-8')

        elif isinstance(data_source, compat.str) and not \
                os.path.exists(data_source):
            return io.StringIO(data_source)

        else:
            stream = io.open(data_source, encoding='utf-8')
            self.openfiles.append(stream)
            return stream

    def get_headers(self, line):
        """Get headers from line."""
        headers = line.rstrip('\n').split(',')
        return headers
