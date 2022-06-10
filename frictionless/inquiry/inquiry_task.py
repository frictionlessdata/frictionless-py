from typing import Optional, List, Any
from ..metadata import Metadata
from ..errors import InquiryError
from ..dialect import Dialect
from ..schema import Schema
from .. import settings


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
        descriptor: Optional[Any] = None,
        *,
        name: Optional[str] = None,
        path: Optional[str] = None,
        scheme: Optional[str] = None,
        format: Optional[str] = None,
        hashing: Optional[str] = None,
        encoding: Optional[str] = None,
        innerpath: Optional[str] = None,
        compression: Optional[str] = None,
        dialect: Optional[Dialect] = None,
        schema: Optional[Schema] = None,
    ):
        self.setinitial("name", name)
        self.setinitial("path", path)
        self.setinitial("scheme", scheme)
        self.setinitial("format", format)
        self.setinitial("hashing", hashing)
        self.setinitial("encoding", encoding)
        self.setinitial("innerpath", innerpath)
        self.setinitial("compression", compression)
        self.setinitial("dialect", dialect)
        self.setinitial("schema", schema)
        super().__init__(descriptor)

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

    # Metadata

    metadata_Error = InquiryError
    metadata_profile = settings.INQUIRY_PROFILE["properties"]["tasks"]["items"]
