from __future__ import annotations
from itertools import chain
from typing import TYPE_CHECKING, Optional, List
from ..exception import FrictionlessException
from ..system import system
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from .loader import Loader
    from .resource import Resource
    from ..interfaces import ICellStream, ISample


class Parser:
    """Parser representation

    Parameters:
        resource (Resource): resource

    """

    requires_loader: bool = False
    supported_types: List[str] = []

    def __init__(self, resource: Resource):
        self.__resource: Resource = resource
        self.__loader: Optional[Loader] = None
        self.__sample: Optional[ISample] = None
        self.__cell_stream: Optional[ICellStream] = None

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
    def cell_stream(self):
        """
        Yields:
            any[][]: list stream
        """
        return self.__cell_stream

    # Open/Close

    def open(self):
        """Open the parser as "io.open" does"""
        self.close()
        try:
            self.__loader = self.read_loader()
            self.__cell_stream = self.read_cell_stream()
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

    def read_cell_stream(self):
        """Read list stream

        Returns:
            gen<any[][]>: list stream
        """
        self.__sample = []
        cell_stream = self.read_cell_stream_create()
        cell_stream = self.read_cell_stream_handle_errors(cell_stream)
        for cells in cell_stream:
            self.__sample.append(cells)
            if len(self.__sample) >= self.resource.detector.sample_size:
                break
        cell_stream = chain(self.__sample, cell_stream)
        return cell_stream

    def read_cell_stream_create(self) -> ICellStream:
        """Create list stream from loader

        Parameters:
            loader (Loader): loader

        Returns:
            gen<any[][]>: list stream
        """
        raise NotImplementedError()

    def read_cell_stream_handle_errors(self, cell_stream):
        """Wrap list stream into error handler

        Parameters:
            gen<any[][]>: list stream

        Returns:
            gen<any[][]>: list stream
        """
        return CellStreamWithErrorHandling(cell_stream)

    # Write

    def write_row_stream(self, source: Resource) -> None:
        """Write row stream from the source resource

        Parameters:
            source (Resource): source resource
        """
        raise NotImplementedError()


# Internal


# NOTE:
# Here we catch some Loader related errors
# We can consider moving it to Loader if it's possible


class CellStreamWithErrorHandling:
    def __init__(self, cell_stream):
        self.cell_stream = cell_stream

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.cell_stream.__next__()
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
