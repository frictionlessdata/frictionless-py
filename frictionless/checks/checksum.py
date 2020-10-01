from .. import errors
from ..check import Check


class ChecksumCheck(Check):
    """Check a table's checksum

    API      | Usage
    -------- | --------
    Public   | `from frictionless import checks`
    Implicit | `validate(checksum={...})`

    Ths check is enabled by default if the `checksum` argument
    is provided for the `validate` function.

    Parameters:
       descriptor (dict): check's descriptor
       descriptor.hash? (str): a hash sum of the table's bytes
       descriptor.bytes? (int): number of bytes
       descriptor.fields? (int): number of fields
       descriptor.rows? (int): number of rows

    """

    possible_Errors = [  # type: ignore
        errors.ChecksumError,
    ]

    # Validate

    def validate_table(self):

        # Hash
        if self.get("hash"):
            hashing = self.table.hashing
            if self["hash"] != self.table.stats["hash"]:
                note = 'expected hash in %s is "%s" and actual is "%s"'
                note = note % (hashing, self["hash"], self.table.stats["hash"])
                yield errors.ChecksumError(note=note)

        # Bytes
        if self.get("bytes"):
            if self["bytes"] != self.table.stats["bytes"]:
                note = 'expected bytes count is "%s" and actual is "%s"'
                note = note % (self["bytes"], self.table.stats["bytes"])
                yield errors.ChecksumError(note=note)

        # Fields
        if self.get("fields"):
            if self["fields"] != self.table.stats["fields"]:
                note = 'expected fields count is "%s" and actual is "%s"'
                note = note % (self["fields"], self.table.stats["fields"])
                yield errors.ChecksumError(note=note)

        # Rows
        if self.get("rows"):
            if self["rows"] != self.table.stats["rows"]:
                note = 'expected rows count is "%s" and actual is "%s"'
                note = note % (self["rows"], self.table.stats["rows"])
                yield errors.ChecksumError(note=note)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "hash": {"type": "string"},
            "bytes": {"type": "number"},
            "fields": {"type": "number"},
            "rows": {"type": "number"},
        },
    }
