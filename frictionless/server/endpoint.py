import attrs
from .project import Project


@attrs.define(kw_only=True)
class Endpoint:
    project: Project
