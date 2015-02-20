# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import codecs
import chardet
from .. import compat


class DataTable(object):

    """Convert a data source into a formatted (csv, json) utf-8 text stream."""

    REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self, data_source, headers=None):
        self.openfiles = []
        self.data_source = data_source
        self.passed_headers = headers
        self.stream = self.to_textstream(self.data_source)
        self.headers, self.values = self.extract(self.passed_headers)

    def replay(self):
        """Replay the stream."""

        if self.stream.seekable():
            self.stream.seek(0)
        else:
            self.stream = self.to_textstream(self.data_source)

        self.headers, self.values = self.extract(self.passed_headers)
        return self.headers, self.values

    def extract(self, headers=None):
        """Extract headers and values from the data stream."""
        headers = headers or self.get_headers(self.stream.readline())
        values = compat.csv_reader(self.stream)
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
            A `self.DEFAULT_ENCODING` encoded text stream (utf-8).

        """

        # textstream = open('tmp.txt', mode='w+t', encoding=self.DEFAULT_ENCODING)
        textstream = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()), encoding=self.DEFAULT_ENCODING)
        self.openfiles.append(textstream)

        if isinstance(data_source, io.IOBase):

            if isinstance(data_source, io.TextIOBase):

                # if not data_source.encoding == self.DEFAULT_ENCODING:
                #    return
                return data_source

            else:

                stream_encoding = self._detect_stream_encoding(data_source)
                textstream = self._decode_to_textstream(data_source, stream_encoding, textstream)

                return textstream

        elif compat.parse.urlparse(data_source).scheme in self.REMOTE_SCHEMES:

            stream = self._stream_from_url(data_source)
            stream_encoding = self._detect_stream_encoding(stream)
            textstream = self._decode_to_textstream(stream, stream_encoding, textstream)

            return textstream

        elif isinstance(data_source, compat.str) and not \
                os.path.exists(data_source):

            stream_encoding = self._detect_stream_encoding(data_source)
            textstream = self._decode_to_textstream(data_source, stream_encoding, textstream)

            return textstream

        else:

            stream = io.open(data_source, mode='r+b')
            self.openfiles.append(stream)
            stream_encoding = self._detect_stream_encoding(stream)
            textstream = self._decode_to_textstream(stream, stream_encoding, textstream)

            return textstream

    def get_headers(self, line):
        """Get headers from line."""
        headers = line.rstrip('\n').split(',')
        return headers

    def _stream_from_url(self, url):
        """Return a seekable and readable stream from a URL."""

        stream = io.BufferedRandom(io.BytesIO())
        stream.write(compat.urlopen(url).read())
        stream.seek(0)

        return stream

    def _detect_stream_encoding(self, stream):
        """Return best guess at encoding of stream."""

        if isinstance(stream, compat.str):
            if isinstance(stream, compat.bytes):
                sample = stream[:2000]
            else:
                sample = compat.to_bytes(stream)[:2000]
        else:
            sample = stream.read(2000)
            stream.seek(0)

        encoding = chardet.detect(sample)['encoding']

        return encoding

    def _decode_to_textstream(self, stream, encoding, textstream):
        """Return a textstream in `self.DEFAULT_ENCODING`"""

        if isinstance(stream, compat.str):
            _stream = io.StringIO()
            _stream.write(stream)
            stream = _stream
            stream.seek(0)
        else:
            stream = codecs.iterdecode(stream, encoding)

        for line in stream:
            recoded = line.encode(self.DEFAULT_ENCODING).decode(self.DEFAULT_ENCODING)
            textstream.write(recoded)

        textstream.seek(0)

        return textstream
