import attrs
from .project import Project


# TODO: rename to Action?
@attrs.define(kw_only=True)
class Endpoint:
    project: Project
