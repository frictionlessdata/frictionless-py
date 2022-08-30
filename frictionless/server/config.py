import attrs


DEFAULT_BASEPATH = ".frictionless/server"


@attrs.define(kw_only=True)
class ServerConfig:
    basepath: str = DEFAULT_BASEPATH
    is_root: bool = False
