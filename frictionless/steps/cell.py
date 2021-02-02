import petl
from ..step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_convert(Step):
    code = "cell-convert"

    def __init__(self, descriptor=None, *, value=None, function=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("function", function)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        field_name = self.get("fieldName")
        function = self.get("function")
        value = self.get("value")
        if not field_name:
            if not function:
                function = lambda input: value
            target.data = source.to_petl().convertall(function)
        elif function:
            target.data = source.to_petl().convert(field_name, function)
        else:
            target.data = source.to_petl().update(field_name, value)

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

    def __init__(self, descriptor=None, *, value=None, field_name=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        self.setinitial("direction", direction)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        value = self.get("value")
        field_name = self.get("fieldName")
        direction = self.get("direction")
        if value:
            target.data = source.to_petl().convert(field_name, {None: value})
        elif direction == "down":
            if field_name:
                target.data = source.to_petl().filldown(field_name)
            else:
                target.data = source.to_petl().filldown()
        elif direction == "right":
            target.data = source.to_petl().fillright()
        elif direction == "left":
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


class cell_format(Step):
    code = "cell-format"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        field_name = self.get("fieldName")
        template = self.get("template")
        if not field_name:
            target.data = source.to_petl().formatall(template)
        else:
            target.data = source.to_petl().format(field_name, template)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }


class cell_interpolate(Step):
    code = "cell-interpolate"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        template = self.get("template")
        field_name = self.get("fieldName")
        if not field_name:
            target.data = source.to_petl().interpolateall(template)
        else:
            target.data = source.to_petl().interpolate(field_name, template)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": ["template"],
        "properties": {
            "template": {"type": "string"},
            "fieldName": {"type": "string"},
        },
    }


class cell_replace(Step):
    code = "cell-replace"

    def __init__(self, descriptor=None, *, pattern=None, replace=None, field_name=None):
        self.setinitial("pattern", pattern)
        self.setinitial("replace", replace)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, source, target):
        pattern = self.get("pattern")
        replace = self.get("replace")
        field_name = self.get("fieldName")
        if not field_name:
            target.data = source.to_petl().replaceall(pattern, replace)
        else:
            pattern = pattern
            function = petl.replace
            if pattern.startswith("<regex>"):
                pattern = pattern.replace("<regex>", "")
                function = petl.sub
            target.data = function(source.to_petl(), field_name, pattern, replace)

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

    def __init__(self, descriptor=None, *, value=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    def transform_resource(self, source, target):
        value = self.get("value")
        field_name = self.get("fieldName")
        target.data = source.to_petl().update(field_name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
