# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import io
import codecs
import datetime
import chardet
import xlrd
from .. import compat


class DataTable(object):

    """Convert a data source into a formatted (csv, json) utf-8 text stream."""

    REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')
    DEFAULT_ENCODING = 'utf-8'
    FORMATS = ('csv', 'excel', 'json')

    def __init__(self, data_source, headers=None, format='csv',
                 encoding=None, header_index=0, excel_sheet_index=0):

        self.openfiles = []
        self.data_source = data_source
        self.passed_headers = headers
        self.format = format
        self.encoding = encoding
        self.header_index = header_index
        self.excel_sheet_index = excel_sheet_index
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
        headers = headers or self.get_headers(self.stream)
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

        if self.format in ('excel', 'json'):
            format_handler = getattr(self, '{0}_data_source'.format(self.format))
            data_source = format_handler(data_source)

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

    def excel_data_source(self, data_source):
        """Get a data_source out of an Excel file."""

        # TODO: Need to flesh out this implementation quite a bit. See messytables

        if compat.parse.urlparse(data_source).scheme in self.REMOTE_SCHEMES:
            instream = compat.urlopen(data_source).read()
            workbook = xlrd.open_workbook(file_contents=instream)
        else:
            workbook = xlrd.open_workbook(data_source)

        out = io.TextIOWrapper(io.BufferedRandom(io.BytesIO()), encoding=self.DEFAULT_ENCODING)

        sheet = workbook.sheet_by_index(self.excel_sheet_index)
        row_count = sheet.nrows

        for row_index in range(row_count):

            values = []

            for cell in sheet.row(row_index):

                # TODO: this is very naive force to string
                if cell.ctype == 3:
                    value = datetime.datetime(
                        *xlrd.xldate_as_tuple(cell.value, sheet.book.datemode)
                    ).isoformat()
                else:
                    value = cell.value

                values.append(compat.str(cell.value))
                _data = ','.join(values)

            out.write('{0}\n'.format(_data))

        out.seek(0)
        return out

    def get_headers(self, stream):
        """Get headers from stream."""

        for index, line in enumerate(stream):
            if index == self.header_index:
                headers = line.rstrip('\n').split(',')
                break

        headers = [h.strip() for h in headers]
        return headers

    def _stream_from_url(self, url):
        """Return a seekable and readable stream from a URL."""

        stream = io.BufferedRandom(io.BytesIO())
        stream.write(compat.urlopen(url).read())
        stream.seek(0)

        return stream

    def _detect_stream_encoding(self, stream):
        """Return best guess at encoding of stream."""

        sample_length = 10000

        if self.encoding:
            return self.encoding

        if isinstance(stream, compat.str):
            if isinstance(stream, compat.bytes):
                sample = stream[:sample_length]
            else:
                sample = compat.to_bytes(stream)[:sample_length]
        else:
            sample = stream.read(sample_length)
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
