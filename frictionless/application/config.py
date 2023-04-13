import attrs
from .. import server


@attrs.define(kw_only=True)
class Config(server.Config):
    pass
