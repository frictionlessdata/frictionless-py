import petl
from ...step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_replace(Step):
    """Replace cell"""

    code = "cell-replace"

    def __init__(self, descriptor=None, *, pattern=None, replace=None, field_name=None):
        self.setinitial("pattern", pattern)
        self.setinitial("replace", replace)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        pattern = self.get("pattern")
        replace = self.get("replace")
        field_name = self.get("fieldName")
        if not field_name:
            resource.data = table.replaceall(pattern, replace)
        else:
            pattern = pattern
            function = petl.replace
            if pattern.startswith("<regex>"):
                pattern = pattern.replace("<regex>", "")
                function = petl.sub
            resource.data = function(table, field_name, pattern, replace)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["pattern"],
        "properties": {
            "pattern": {"type": "string"},
            "replace": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }
