from .exception import FrictionlessException
from .system import system
from . import errors
from . import config


class Parser:
    """Parser representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Parser`

    Parameters:
        resource (Resource): resource

    """

    # TODO: can we get rid of newline and needs_loader?
    newline = None
    needs_loader = True
    supported_types = []

    def __init__(self, resource):
        self.__resource = resource
        self.__loader = None
        self.__data_stream = None
        if self.newline is not None:
            self.__resource.control.newline = self.newline

    def __enter__(self):
        if self.closed:
            self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    @property
    def resource(self):
        """
        Returns:
            Resource: resource
        """
        return self.__resource

    @property
    def loader(self):
        """
        Returns:
            Loader: loader
        """
        return self.__loader

    @property
    def data_stream(self):
        """
        Yields:
            any[][]: data stream
        """
        return self.__data_stream

    # Open/Close

    def open(self):
        """Open the parser as "io.open" does"""
        self.close()
        if self.__resource.dialect.metadata_errors:
            error = self.__resource.dialect.metadata_errors[0]
            raise FrictionlessException(error)
        try:
            self.__loader = self.read_loader()
            self.__data_stream = self.read_data_stream()
            return self
        except Exception:
            self.close()
            raise

    def close(self):
        """Close the parser as "filelike.close" does"""
        if self.__loader:
            self.__loader.close()

    @property
    def closed(self):
        """Whether the parser is closed

        Returns:
            bool: if closed
        """
        return self.__loader is None

    # Read

    def read_loader(self):
        """Create and open loader

        Returns:
            Loader: loader
        """
        if self.needs_loader:
            loader = system.create_loader(self.resource)
            return loader.open()

    def read_data_stream(self):
        """Read data stream

        Returns:
            gen<any[][]>: data stream
        """
        data_stream = self.read_data_stream_create()
        data_stream = self.read_data_stream_handle_errors(data_stream)
        return data_stream

    def read_data_stream_create(self, loader):
        """Create data stream from loader

        Parameters:
            loader (Loader): loader

        Returns:
            gen<any[][]>: data stream
        """
        raise NotImplementedError()

    def read_data_stream_handle_errors(self, data_stream):
        """Wrap data stream into error handler

        Parameters:
            gen<any[][]>: data stream

        Returns:
            gen<any[][]>: data stream
        """
        return DataStreamWithErrorHandling(data_stream)

    # Write

    def write_row_stream(self, read_row_stream):
        """Write row stream into the resource

        Parameters:
            read_row_stream (gen<Row[]>): row stream factory
        """
        read_row_stream = self.write_row_stream_create(read_row_stream)
        result = self.write_row_stream_save(read_row_stream)
        return result

    def write_row_stream_create(self, read_row_stream):
        return read_row_stream

    def write_row_stream_save(self, read_row_stream):
        raise NotImplementedError()


# Internal


# TODO:
# Here we catch some Loader related errors
# We can consider moving it to Loader if it's possible
class DataStreamWithErrorHandling:
    def __init__(self, data_stream):
        self.data_stream = data_stream

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.data_stream.__next__()
        except StopIteration:
            raise
        except FrictionlessException:
            raise
        except config.COMPRESSION_EXCEPTIONS as exception:
            error = errors.CompressionError(note=str(exception))
            raise FrictionlessException(error)
        except UnicodeDecodeError as exception:
            error = errors.EncodingError(note=str(exception))
            raise FrictionlessException(error) from exception
        except Exception as exception:
            error = errors.SourceError(note=str(exception))
            raise FrictionlessException(error) from exception
