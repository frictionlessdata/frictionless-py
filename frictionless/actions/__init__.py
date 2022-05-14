from .describe import describe
from .extract import extract
from .transform import transform
from .validate import validate

# TODO: remove these legacy imports in v5
from .describe import (
    describe_dialect,
    describe_resource,
    describe_package,
    describe_schema,
)
from .extract import extract_resource, extract_package
from .transform import transform_resource, transform_package, transform_pipeline
from .validate import (
    validate_inquiry,
    validate_resource,
    validate_package,
    validate_schema,
)
