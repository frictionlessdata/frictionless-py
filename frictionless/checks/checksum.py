from .. import errors
from ..check import Check


class checksum(Check):
    """Check a table's checksum

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checksum={...})`

    Ths check is enabled by default if the `checksum` argument
    is provided for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       hash? (str): a hash sum of the table's bytes
       bytes? (int): number of bytes
       fields? (int): number of fields
       rows? (int): number of rows

    """

    code = "checksum"
    Errors = [errors.ChecksumError]

    def __init__(self, descriptor=None, *, hash=None, bytes=None, fields=None, rows=None):
        self.setinitial("hash", hash)
        self.setinitial("bytes", bytes)
        self.setinitial("fields", fields)
        self.setinitial("rows", rows)
        super().__init__(descriptor)

    # Validate

    def validate_table(self):

        # Hash
        if self.get("hash"):
            hashing = self.resource.hashing
            if self["hash"] != self.resource.stats["hash"]:
                note = 'expected hash in %s is "%s" and actual is "%s"'
                note = note % (hashing, self["hash"], self.resource.stats["hash"])
                yield errors.ChecksumError(note=note)

        # Bytes
        if self.get("bytes"):
            if self["bytes"] != self.resource.stats["bytes"]:
                note = 'expected bytes count is "%s" and actual is "%s"'
                note = note % (self["bytes"], self.resource.stats["bytes"])
                yield errors.ChecksumError(note=note)

        # Fields
        if self.get("fields"):
            if self["fields"] != self.resource.stats["fields"]:
                note = 'expected fields count is "%s" and actual is "%s"'
                note = note % (self["fields"], self.resource.stats["fields"])
                yield errors.ChecksumError(note=note)

        # Rows
        if self.get("rows"):
            if self["rows"] != self.resource.stats["rows"]:
                note = 'expected rows count is "%s" and actual is "%s"'
                note = note % (self["rows"], self.resource.stats["rows"])
                yield errors.ChecksumError(note=note)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "properties": {
            "hash": {"type": "string"},
            "bytes": {"type": "number"},
            "fields": {"type": "number"},
            "rows": {"type": "number"},
        },
    }
