from typing import Optional
from ..metadata import Metadata
from ..checklist import Checklist
from ..dialect import Dialect
from ..schema import Schema
from ..file import File
from .. import settings
from .. import errors


# TODO: support data?
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
        self.setinitial("descriptor", descriptor)
        self.setinitial("type", type)
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
        self.setinitial("checklist", checklist)
        super().__init__()

    @property
    def descriptor(self):
        """
        Returns:
            any: descriptor
        """
        return self.get("descriptor")

    @property
    def type(self) -> str:
        """
        Returns:
            any: type
        """
        type = self.get("type")
        if not type:
            type = "resource"
            if self.descriptor:
                file = File(self.descriptor)
                type = "package" if file.type == "package" else "resource"
        return type

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
    def compression(self):
        """
        Returns:
            any: compression
        """
        return self.get("compression")

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

    @property
    def checklist(self):
        """
        Returns:
            any: checklist
        """
        return self.get("checklist")

    # Import/Export

    @staticmethod
    # TODO: recover after a cyclic dep is resolved
    #  def from_descriptor(descriptor: IDescriptor):
    def from_descriptor(descriptor: dict):
        metadata = Metadata(descriptor)
        dialect = Dialect(metadata.get("dialect", {}))
        schema = Schema(metadata.get("schema", {}))
        checklist = Checklist(metadata.get("checklist", {}))
        return InquiryTask(
            descriptor=metadata.get("descriptor"),  # type: ignore
            type=metadata.get("type"),  # type: ignore
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
            checklist=checklist or None,
        )

    # Metadata

    metadata_Error = errors.InquiryError
    metadata_profile = settings.INQUIRY_PROFILE["properties"]["tasks"]["items"]

    def metadata_validate(self):
        yield from super().metadata_validate()

        # TODO: validate type/descriptor
