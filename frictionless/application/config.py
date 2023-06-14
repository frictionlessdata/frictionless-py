import attrs
from .. import server


@attrs.define(kw_only=True, repr=False)
class Config(server.Config):
    pass
