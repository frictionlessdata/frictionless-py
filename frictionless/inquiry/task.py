from typing import TYPE_CHECKING, Optional
from ..metadata import Metadata
from ..dialect import Dialect
from ..schema import Schema
from .. import settings
from .. import errors

if TYPE_CHECKING:
    from ..interfaces import IDescriptor


# TODO: support descriptor
# TODO: split into ResourceInquiryTask/PackageInqiuryTask?


class InquiryTask(Metadata):
    """Inquiry task representation.

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        path: str,
        name: Optional[str] = None,
        scheme: Optional[str] = None,
        format: Optional[str] = None,
        hashing: Optional[str] = None,
        encoding: Optional[str] = None,
        innerpath: Optional[str] = None,
        compression: Optional[str] = None,
        dialect: Optional[Dialect] = None,
        schema: Optional[Schema] = None,
    ):
        self.setinitial("path", path)
        self.setinitial("name", name)
        self.setinitial("scheme", scheme)
        self.setinitial("format", format)
        self.setinitial("hashing", hashing)
        self.setinitial("encoding", encoding)
        self.setinitial("innerpath", innerpath)
        self.setinitial("compression", compression)
        self.setinitial("dialect", dialect)
        self.setinitial("schema", schema)
        super().__init__()

    @property
    def name(self):
        """
        Returns:
            any: name
        """
        return self.get("name")

    @property
    def path(self):
        """
        Returns:
            any: path
        """
        return self.get("path")

    @property
    def scheme(self):
        """
        Returns:
            any: scheme
        """
        return self.get("scheme")

    @property
    def format(self):
        """
        Returns:
            any: format
        """
        return self.get("format")

    @property
    def hashing(self):
        """
        Returns:
            any: hashing
        """
        return self.get("hashing")

    @property
    def encoding(self):
        """
        Returns:
            any: encoding
        """
        return self.get("encoding")

    @property
    def innerpath(self):
        """
        Returns:
            any: innerpath
        """
        return self.get("innerpath")

    @property
    def compresion(self):
        """
        Returns:
            any: compresion
        """
        return self.get("compresion")

    @property
    def dialect(self):
        """
        Returns:
            any: dialect
        """
        return self.get("dialect")

    @property
    def schema(self):
        """
        Returns:
            any: schema
        """
        return self.get("schema")

    # Import/Export

    @staticmethod
    def from_descriptor(descriptor: IDescriptor):
        metadata = Metadata(descriptor)
        dialect = Dialect(metadata.get("dialect", {}))
        schema = Schema(metadata.get("schema", {}))
        return InquiryTask(
            name=metadata.get("name"),  # type: ignore
            path=metadata.get("path"),  # type: ignore
            scheme=metadata.get("scheme"),  # type: ignore
            format=metadata.get("format"),  # type: ignore
            hashing=metadata.get("hashing"),  # type: ignore
            encoding=metadata.get("encoding"),  # type: ignore
            innerpath=metadata.get("innerpath"),  # type: ignore
            compression=metadata.get("compression"),  # type: ignore
            dialect=dialect or None,
            schema=schema or None,
        )

    # Metadata

    metadata_Error = errors.InquiryError
    metadata_profile = settings.INQUIRY_PROFILE["properties"]["tasks"]["items"]
