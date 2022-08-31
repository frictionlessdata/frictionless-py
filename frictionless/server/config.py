import attrs


DEFAULT_BASEPATH = ".server"


@attrs.define(kw_only=True)
class Config:
    basepath: str = DEFAULT_BASEPATH
    root: bool = False
