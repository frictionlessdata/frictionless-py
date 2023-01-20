import attrs


# TODO: rebase on metadata class?
# TODO: add partial
@attrs.define(kw_only=True)
class Record:
    name: str
    path: str
    updated: float
    resource: dict
    report: dict

    def to_descriptor(self):
        return attrs.asdict(self)
