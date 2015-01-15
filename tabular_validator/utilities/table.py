import os
import io
import csv
from urllib import parse, request


class DataTable(object):

    """Convert a data source into a formatted (csv, json) utf-8 text stream."""

    REMOTE_SCHEMES = ('http', 'https', 'ftp', 'ftps')

    def __init__(self, data_source, headers=None):

        self._openfiles = []
        self.stream = self.to_textstream(data_source)
        self.headers, self.values = self.extract(headers)

    def extract(self, headers=None):

        # TODO: Support headers at any index, with any delimiter and associated
        headers = headers or self.get_headers(self.stream.readline())
        # TODO: json, accept hints for start of stream data, etc.
        values = csv.reader(self.stream)
        # reset the stream for others to possibly consume
        self.stream.seek(0)
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

        elif parse.urlparse(data_source).scheme in self.REMOTE_SCHEMES:
            f, h = request.urlretrieve(data_source)
            stream = io.open(f, encoding='utf-8')
            self._openfiles.append(stream)
            return stream

        elif isinstance(data_source, str) and not os.path.exists(data_source):
            return io.StringIO(data_source)

        else:
            stream = io.open(data_source, encoding='utf-8')
            self._openfiles.append(stream)
            return stream

    def get_headers(self, line):
        """Get headers from line."""
        headers = line.rstrip('\n').split(',')
        return headers
