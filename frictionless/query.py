from .metadata import Metadata
from . import helpers
from . import errors


class Query(Metadata):
    """Query representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless import Query`

    Parameters:
        descriptor? (str|dict): query descriptor
        pick_fields? ((str|int)[]): what fields to pick
        skip_fields? ((str|int)[]): what fields to skip
        limit_fields? (int): amount of fields
        offset_fields? (int): from what field to start
        pick_rows? ((str|int)[]): what rows to pick
        skip_rows? ((str|int)[]): what rows to skip
        limit_rows? (int): amount of rows
        offset_rows? (int): from what row to start

    """

    def __init__(
        self,
        descriptor=None,
        *,
        pick_fields=None,
        skip_fields=None,
        limit_fields=None,
        offset_fields=None,
        pick_rows=None,
        skip_rows=None,
        limit_rows=None,
        offset_rows=None,
    ):
        self.setinitial("pickFields", pick_fields)
        self.setinitial("skipFields", skip_fields)
        self.setinitial("limitFields", limit_fields)
        self.setinitial("offsetFields", offset_fields)
        self.setinitial("pickRows", pick_rows)
        self.setinitial("skipRows", skip_rows)
        self.setinitial("limitRows", limit_rows)
        self.setinitial("offsetRows", offset_rows)
        super().__init__(descriptor)

    @Metadata.property
    def pick_fields(self):
        """
        Returns:
            (str|int)[]?: pick fields
        """
        return self.get("pickFields")

    @Metadata.property
    def skip_fields(self):
        """
        Returns:
            (str|int)[]?: skip fields
        """
        return self.get("skipFields")

    @Metadata.property
    def limit_fields(self):
        """
        Returns:
            int?: limit fields
        """
        return self.get("limitFields")

    @Metadata.property
    def offset_fields(self):
        """
        Returns:
            int?: offset fields
        """
        return self.get("offsetFields")

    @Metadata.property
    def pick_rows(self):
        """
        Returns:
            (str|int)[]?: pick rows
        """
        return self.get("pickRows")

    @Metadata.property
    def skip_rows(self):
        """
        Returns:
            (str|int)[]?: skip rows
        """
        return self.get("skipRows")

    @Metadata.property
    def limit_rows(self):
        """
        Returns:
            int?: limit rows
        """
        return self.get("limitRows")

    @Metadata.property
    def offset_rows(self):
        """
        Returns:
            int?: offset rows
        """
        return self.get("offsetRows")

    @Metadata.property(write=False)
    def is_field_filtering(self):
        """
        Returns:
            bool: whether there is a field filtering
        """
        return (
            self.pick_fields is not None
            or self.skip_fields is not None
            or self.limit_fields is not None
            or self.offset_fields is not None
        )

    @Metadata.property(write=False)
    def pick_fields_compiled(self):
        """
        Returns:
            re?: compiled pick fields
        """
        return helpers.compile_regex(self.pick_fields)

    @Metadata.property(write=False)
    def skip_fields_compiled(self):
        """
        Returns:
            re?: compiled skip fields
        """
        return helpers.compile_regex(self.skip_fields)

    @Metadata.property(write=False)
    def pick_rows_compiled(self):
        """
        Returns:
            re?: compiled pick rows
        """
        return helpers.compile_regex(self.pick_rows)

    @Metadata.property(write=False)
    def skip_rows_compiled(self):
        """
        Returns:
            re?: compiled skip fields
        """
        return helpers.compile_regex(self.skip_rows)

    # Expand

    def expand(self):
        """Expand metadata"""
        pass

    # Metadata

    metadata_Error = errors.QueryError
    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "pickFields": {"type": "array"},
            "skipFields": {"type": "array"},
            "limitFields": {"type": "number", "minimum": 1},
            "offsetFields": {"type": "number", "minimum": 1},
            "pickRows": {"type": "array"},
            "skipRows": {"type": "array"},
            "limitRows": {"type": "number", "minimum": 1},
            "offsetRows": {"type": "number", "minimum": 1},
        },
    }
