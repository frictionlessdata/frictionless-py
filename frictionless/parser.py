from itertools import chain
from .exception import FrictionlessException
from .system import system
from . import settings
from . import errors


class Parser:
    """Parser representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Parser`

    Parameters:
        resource (Resource): resource

    """

    requires_loader = False
    supported_types = []

    def __init__(self, resource):
        self.__resource = resource
        self.__loader = None
        self.__sample = None
        self.__list_stream = None

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
    def sample(self):
        """
        Returns:
            Loader: sample
        """
        return self.__sample

    @property
    def list_stream(self):
        """
        Yields:
            any[][]: list stream
        """
        return self.__list_stream

    # Open/Close

    def open(self):
        """Open the parser as "io.open" does"""
        self.close()
        try:
            self.__loader = self.read_loader()
            self.__list_stream = self.read_list_stream()
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
        if self.requires_loader:
            loader = system.create_loader(self.resource)
            return loader.open()

    def read_list_stream(self):
        """Read list stream

        Returns:
            gen<any[][]>: list stream
        """
        self.__sample = []
        list_stream = self.read_list_stream_create()
        list_stream = self.read_list_stream_handle_errors(list_stream)
        for cells in list_stream:
            self.__sample.append(cells)
            if len(self.__sample) >= self.resource.detector.sample_size:
                break
        list_stream = chain(self.__sample, list_stream)
        return list_stream

    def read_list_stream_create(self):
        """Create list stream from loader

        Parameters:
            loader (Loader): loader

        Returns:
            gen<any[][]>: list stream
        """
        raise NotImplementedError()

    def read_list_stream_handle_errors(self, list_stream):
        """Wrap list stream into error handler

        Parameters:
            gen<any[][]>: list stream

        Returns:
            gen<any[][]>: list stream
        """
        return ListStreamWithErrorHandling(list_stream)

    # Write

    def write_row_stream(self, resource):
        """Write row stream from the source resource

        Parameters:
            source (Resource): source resource
        """
        raise NotImplementedError()


# Internal


# NOTE:
# Here we catch some Loader related errors
# We can consider moving it to Loader if it's possible


class ListStreamWithErrorHandling:
    def __init__(self, list_stream):
        self.list_stream = list_stream

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.list_stream.__next__()
        except StopIteration:
            raise
        except FrictionlessException:
            raise
        except settings.COMPRESSION_EXCEPTIONS as exception:
            error = errors.CompressionError(note=str(exception))
            raise FrictionlessException(error)
        except UnicodeDecodeError as exception:
            error = errors.EncodingError(note=str(exception))
            raise FrictionlessException(error) from exception
        except Exception as exception:
            error = errors.SourceError(note=str(exception))
            raise FrictionlessException(error) from exception
