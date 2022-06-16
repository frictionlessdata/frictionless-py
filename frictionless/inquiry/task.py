from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from ..metadata2 import Metadata2
from ..checklist import Checklist
from ..dialect import Dialect
from ..schema import Schema
from ..file import File
from .. import settings
from .. import helpers
from .. import errors

if TYPE_CHECKING:
    from ..interfaces import IDescriptor, IResolvedDescriptor


class InquiryTask(Metadata2):
    """Inquiry task representation.

    Parameters:
        descriptor? (str|dict): descriptor

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(
        self,
        descriptor: Optional[str] = None,
        type: Optional[str] = None,
        path: Optional[str] = None,
        name: Optional[str] = None,
        scheme: Optional[str] = None,
        format: Optional[str] = None,
        hashing: Optional[str] = None,
        encoding: Optional[str] = None,
        innerpath: Optional[str] = None,
        compression: Optional[str] = None,
        dialect: Optional[Dialect] = None,
        schema: Optional[Schema] = None,
        checklist: Optional[Checklist] = None,
    ):
        self.descriptor = descriptor
        self.path = path
        self.name = name
        self.scheme = scheme
        self.format = format
        self.hashing = hashing
        self.encoding = encoding
        self.innerpath = innerpath
        self.compression = compression
        self.dialect = dialect
        self.schema = schema
        self.checklist = checklist
        self.__type = type

    descriptor: Optional[str]
    """# TODO: add docs"""

    path: Optional[str]
    """# TODO: add docs"""

    name: Optional[str]
    """# TODO: add docs"""

    scheme: Optional[str]
    """# TODO: add docs"""

    format: Optional[str]
    """# TODO: add docs"""

    hashing: Optional[str]
    """# TODO: add docs"""

    encoding: Optional[str]
    """# TODO: add docs"""

    innerpath: Optional[str]
    """# TODO: add docs"""

    compression: Optional[str]
    """# TODO: add docs"""

    dialect: Optional[Dialect]
    """# TODO: add docs"""

    schema: Optional[Schema]
    """# TODO: add docs"""

    checklist: Optional[Checklist]
    """# TODO: add docs"""

    @property
    def type(self) -> str:
        """
        Returns:
            any: type
        """
        type = self.__type
        if not type:
            type = "resource"
            if self.descriptor:
                file = File(self.descriptor)
                type = "package" if file.type == "package" else "resource"
        return type

    @type.setter
    def type(self, value: str):
        self.__type = value

    # Import/Export

    @classmethod
    def from_descriptor(cls, descriptor: IDescriptor):
        mapping = cls.metadata_extract(descriptor)
        dialect = Dialect(mapping.get("dialect", {}))
        schema = Schema(mapping.get("schema", {}))
        checklist = Checklist(mapping.get("checklist", {}))
        return InquiryTask(
            descriptor=mapping.get("descriptor"),  # type: ignore
            type=mapping.get("type"),  # type: ignore
            name=mapping.get("name"),  # type: ignore
            path=mapping.get("path"),  # type: ignore
            scheme=mapping.get("scheme"),  # type: ignore
            format=mapping.get("format"),  # type: ignore
            hashing=mapping.get("hashing"),  # type: ignore
            encoding=mapping.get("encoding"),  # type: ignore
            innerpath=mapping.get("innerpath"),  # type: ignore
            compression=mapping.get("compression"),  # type: ignore
            dialect=dialect or None,
            schema=schema or None,
            checklist=checklist or None,
        )

    def to_descriptor(self) -> IResolvedDescriptor:
        descriptor: IResolvedDescriptor = dict(
            type=self.type,
            name=self.name,
            path=self.path,
            scheme=self.scheme,
            format=self.format,
            hashing=self.hashing,
            encoding=self.encoding,
            innerpath=self.innerpath,
            compression=self.compression,
        )
        # TODO: rebase on to_descriptor
        if self.dialect:
            descriptor["dialect"] = self.dialect.to_dict()
        if self.schema:
            descriptor["schema"] = self.schema.to_dict()
        if self.checklist:
            descriptor["checklist"] = self.checklist.to_dict()
        return helpers.remove_non_values(descriptor)

    # Metadata

    metadata_Error = errors.InquiryError
    metadata_profile = settings.INQUIRY_PROFILE["properties"]["tasks"]["items"]

    def metadata_validate(self):
        yield from super().metadata_validate()

        # TODO: validate type/descriptor
