from dataclasses import dataclass
from ...pipeline import Step


# NOTE:
# We need to review simpleeval perfomance for using it with row_filter
# Currently, metadata profiles are not fully finished; will require improvements


@dataclass
class row_subset(Step):
    """Subset rows"""

    code = "row-subset"

    # Properties

    subset: str
    """TODO: add docs"""

    field_name: str
    """TODO: add docs"""

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        if self.subset == "conflicts":
            resource.data = table.conflicts(self.field_name)  # type: ignore
        elif self.subset == "distinct":
            resource.data = table.distinct(self.field_name)  # type: ignore
        elif self.subset == "duplicates":
            resource.data = table.duplicates(self.field_name)  # type: ignore
        elif self.subset == "unique":
            resource.data = table.unique(self.field_name)  # type: ignore

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["subset"],
        "properties": {
            "code": {},
            "subset": {
                "type": "string",
                "enum": ["conflicts", "distinct", "duplicates", "unique"],
            },
            "fieldName": {"type": "string"},
        },
    }
