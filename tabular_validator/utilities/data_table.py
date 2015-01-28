# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import csv
import requests
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

        headers = headers or self.get_headers(self.stream.readline())
        values = csv.reader(self.stream, quotechar="'")

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

        Raises:
            IOError: if this
            ValueError: if that
        """

        # TODO: always coerce to utf-8 encoded text streams
        # TODO: Handle various errors (open file, http errors, etc.)

        if isinstance(data_source, io.IOBase):
            return data_source

        elif compat.parse.urlparse(data_source).scheme in self.REMOTE_SCHEMES:
            with compat.NamedTemporaryFile(mode='w+t', encoding='utf-8') as tmp:
                tmp.write(requests.get(data_source).text)
                stream = io.open(tmp.name, encoding='utf-8')
            return stream

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
