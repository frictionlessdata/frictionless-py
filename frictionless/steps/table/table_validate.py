from ...step import Step
from ...exception import FrictionlessException


# NOTE:
# We might consider implementing table_preload/cache step
# Some of the following step use **options - we need to review/fix it
# Currently, metadata profiles are not fully finished; will require improvements
# We need to review table_pivot step as it's not fully implemented/tested
# We need to review table_validate step as it's not fully implemented/tested
# We need to review table_write step as it's not fully implemented/tested
# We need to review how we use "target.schema.fields.clear()"


class table_validate(Step):
    """Validate table"""

    code = "table-validate"

    # Transform

    def transform_resource(self, resource):
        current = resource.to_copy()

        # Data
        def data():
            with current:
                if not current.header.valid:
                    raise FrictionlessException(error=current.header.errors[0])
                yield current.header
                for row in current.row_stream:
                    if not row.valid:
                        raise FrictionlessException(error=row.errors[0])
                    yield row

        # Meta
        resource.data = data

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {},
    }
