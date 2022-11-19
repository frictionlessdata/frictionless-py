from __future__ import annotations
from itertools import chain
from typing import TYPE_CHECKING, ClassVar, Optional, List
from ..exception import FrictionlessException
from ..platform import platform
from .system import system
from .. import errors

if TYPE_CHECKING:
    from .loader import Loader
    from ..resource import Resource
    from ..interfaces import ICellStream, ISample


class Parser:
    """Parser representation

    Parameters:
        resource (Resource): resource

    """

    requires_loader: ClassVar[bool] = False
    """
    Specifies if parser requires the loader to load the
    data.
    """

    supported_types: ClassVar[List[str]] = []
    """
    Data types supported by the parser.
    """

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

    # Props

    @property
    def resource(self) -> Resource:
        """
        Returns:
            Resource: resource
        """
        return self.__resource

    @property
    def loader(self) -> Loader:
        """
        Returns:
            Loader: loader
        """
        if self.__loader is None:
            raise FrictionlessException("parser is not open or non requiring loader")
        return self.__loader

    @property
    def sample(self) -> ISample:
        """
        Returns:
            Loader: sample
        """
        if self.__sample is None:
            raise FrictionlessException("parser is not open")
        return self.__sample

    @property
    def cell_stream(self) -> ICellStream:
        """
        Yields:
            any[][]: list stream
        """
        if self.__cell_stream is None:
            raise FrictionlessException("parser is not open")
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

    def close(self) -> None:
        """Close the parser as "filelike.close" does"""
        if self.__loader:
            self.__loader.close()

    @property
    def closed(self) -> bool:
        """Whether the parser is closed

        Returns:
            bool: if closed
        """
        return self.__loader is None

    # Read

    def read_loader(self) -> Optional[Loader]:
        """Create and open loader

        Returns:
            Loader: loader
        """
        if self.requires_loader:
            loader = system.create_loader(self.resource)
            return loader.open()

    def read_cell_stream(self) -> ICellStream:
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

    def read_cell_stream_handle_errors(
        self,
        cell_stream: ICellStream,
    ) -> CellStreamWithErrorHandling:
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
    def __init__(self, cell_stream: ICellStream):
        self.cell_stream = cell_stream

    def __iter__(self):
        return self

    def __next__(self):
        try:
            return self.cell_stream.__next__()  # type: ignore
        except StopIteration:
            raise
        except FrictionlessException:
            raise
        except (platform.zipfile.BadZipFile, platform.gzip.BadGzipFile) as exception:
            error = errors.CompressionError(note=str(exception))
            raise FrictionlessException(error)
        except UnicodeDecodeError as exception:
            error = errors.EncodingError(note=str(exception))
            raise FrictionlessException(error) from exception
        except Exception as exception:
            error = errors.SourceError(note=str(exception))
            raise FrictionlessException(error) from exception
