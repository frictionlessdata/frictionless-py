import petl
from ..step import Step


# NOTE:
# Some of the following step can support WHERE/PREDICAT arguments (see petl)
# Currently, metadata profiles are not fully finished; will require improvements


class cell_convert(Step):
    """Convert cell"""

    code = "cell-convert"

    def __init__(self, descriptor=None, *, value=None, function=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("function", function)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field_name = self.get("fieldName")
        function = self.get("function")
        value = self.get("value")
        if not field_name:
            if not function:
                function = lambda input: value
            resource.data = table.convertall(function)
        elif function:
            resource.data = table.convert(field_name, function)
        else:
            resource.data = table.update(field_name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "value": {},
            "fieldName": {"type": "string"},
        },
    }


class cell_fill(Step):
    """Fill cell"""

    code = "cell-fill"

    def __init__(self, descriptor=None, *, value=None, field_name=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        self.setinitial("direction", direction)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        value = self.get("value")
        field_name = self.get("fieldName")
        direction = self.get("direction")
        if value:
            resource.data = table.convert(field_name, {None: value})
        elif direction == "down":
            if field_name:
                resource.data = table.filldown(field_name)
            else:
                resource.data = table.filldown()
        elif direction == "right":
            resource.data = table.fillright()
        elif direction == "left":
            resource.data = table.fillleft()

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
    """Format cell"""

    code = "cell-format"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        field_name = self.get("fieldName")
        template = self.get("template")
        if not field_name:
            resource.data = table.formatall(template)
        else:
            resource.data = table.format(field_name, template)

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
    """Interpolate cell"""

    code = "cell-interpolate"

    def __init__(self, descriptor=None, *, template=None, field_name=None):
        self.setinitial("template", template)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        template = self.get("template")
        field_name = self.get("fieldName")
        table = resource.to_petl()
        if not field_name:
            resource.data = table.interpolateall(template)
        else:
            resource.data = table.interpolate(field_name, template)

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
    """Replace cell"""

    code = "cell-replace"

    def __init__(self, descriptor=None, *, pattern=None, replace=None, field_name=None):
        self.setinitial("pattern", pattern)
        self.setinitial("replace", replace)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    # Transform

    def transform_resource(self, resource):
        table = resource.to_petl()
        pattern = self.get("pattern")
        replace = self.get("replace")
        field_name = self.get("fieldName")
        if not field_name:
            resource.data = table.replaceall(pattern, replace)
        else:
            pattern = pattern
            function = petl.replace
            if pattern.startswith("<regex>"):
                pattern = pattern.replace("<regex>", "")
                function = petl.sub
            resource.data = function(table, field_name, pattern, replace)

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
    """Set cell"""

    code = "cell-set"

    def __init__(self, descriptor=None, *, value=None, field_name=None):
        self.setinitial("value", value)
        self.setinitial("fieldName", field_name)
        super().__init__(descriptor)

    def transform_resource(self, resource):
        table = resource.to_petl()
        value = self.get("value")
        field_name = self.get("fieldName")
        resource.data = table.update(field_name, value)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "required": [],
        "properties": {
            "fieldName": {"type": "string"},
            "value": {},
        },
    }
