import petl
from ..step import Step


# TODO: accept WHERE/PREDICAT clause
class cell_convert(Step):
    code = "cell-convert"

    def __init__(self, descriptor=None, *, value=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__value = value
        self.__field_name = field_name

    # Transform

    def transform_resource(self, source, target):
        value = self["value"]
        if not self.__field_name:
            if not callable(value):
                value = lambda val: self.__value
            target.data = source.to_petl().convertall(value)
        else:
            if not callable(value):
                target.data = source.to_petl().update(self.__field_name, value)
            else:
                target.data = source.to_petl().convert(self.__field_name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["value"],
        "properties": {
            "value": {},
            "fieldName": {"type": "string"},
        },
    }


class cell_fill(Step):
    code = "cell-fill"

    def __init__(self, descriptor=None, *, field_name=None, value=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.setinitial("fieldName", field_name)
        self.setinitial("value", value)
        self.setinitial("direction", direction)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__field_name = field_name
        self.__value = value
        self.__direction = direction

    # Transform

    def transform_resource(self, source, target):
        if self.__value:
            target.data = source.to_petl().convert(
                self.__field_name, {None: self.__value}
            )
        elif self.__direction == "down":
            if self.__field_name:
                target.data = source.to_petl().filldown(self.__field_name)
            else:
                target.data = source.to_petl().filldown()
        elif self.__direction == "right":
            target.data = source.to_petl().fillright()
        elif self.__direction == "left":
            target.data = source.to_petl().fillleft()

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
            "direction": {},
        },
    }


# TODO: accept WHERE/PREDICAT clause
class cell_format(Step):
    code = "cell-format"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__template = template
        self.__field_name = field_name

    # Transform

    def transform_resource(self, source, target):
        if not self.__field_name:
            target.data = source.to_petl().formatall(self.__template)
        else:
            target.data = source.to_petl().format(self.__field_name, self.__template)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }


# TODO: accept WHERE/PREDICAT clause
class cell_interpolate(Step):
    code = "cell-interpolate"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__template = template
        self.__field_name = field_name

    # Transform

    def transform_resource(self, source, target):
        if not self.__field_name:
            target.data = source.to_petl().interpolateall(self.__template)
        else:
            target.data = source.to_petl().interpolate(self.__field_name, self.__template)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }


# TODO: accept WHERE/PREDICAT clause
class cell_replace(Step):
    code = "cell-replace"

    def __init__(self, descriptor=None, *, pattern=None, replace=None, field_name=None):
        self.setinitial("pattern", pattern)
        self.setinitial("replace", replace)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__pattern = pattern
        self.__replace = replace
        self.__field_name = field_name

    # Transform

    def transform_resource(self, source, target):
        if not self.__field_name:
            target.data = source.to_petl().replaceall(self.__pattern, self.__replace)
        else:
            pattern = self.__pattern
            function = petl.replace
            if self.__pattern.startswith("<regex>"):
                pattern = pattern.replace("<regex>", "")
                function = petl.sub
            target.data = function(
                source.to_petl(), self.__field_name, pattern, self.__replace
            )

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["pattern"],
        "properties": {
            "pattern": {"type": "string"},
            "replace": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }


class cell_set(Step):
    code = "cell-set"

    def __init__(self, descriptor=None, *, field_name=None, value=None):
        self.setinitial("fieldName", field_name)
        self.setinitial("value", value)
        super().__init__(descriptor)
        # TODO: reimplement
        self.__field_name = self.get("fieldName")
        self.__value = self.get("value")

    def transform_resource(self, source, target):
        target.data = source.to_petl().update(self.__field_name, self.__value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
