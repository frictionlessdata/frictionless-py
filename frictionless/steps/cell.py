import petl
from ..step import Step


# TODO: accept WHERE/PREDICAT clause
class cell_convert(Step):
    def __init__(self, *, value, field_name=None):
        self.__value = value
        self.__field_name = field_name

    def transform_resource(self, source, target):
        value = self.__value
        if not self.__field_name:
            if not callable(value):
                value = lambda val: self.__value
            target.data = source.to_petl().convertall(value)
        else:
            if not callable(value):
                target.data = source.to_petl().update(self.__field_name, value)
            else:
                target.data = source.to_petl().convert(self.__field_name, value)


class cell_fill(Step):
    def __init__(self, *, field_name=None, value=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.__field_name = field_name
        self.__value = value
        self.__direction = direction

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


# TODO: accept WHERE/PREDICAT clause
class cell_format(Step):
    def __init__(self, *, template, field_name=None):
        self.__template = template
        self.__field_name = field_name

    def transform_resource(self, source, target):
        if not self.__field_name:
            target.data = source.to_petl().formatall(self.__template)
        else:
            target.data = source.to_petl().format(self.__field_name, self.__template)


# TODO: accept WHERE/PREDICAT clause
class cell_interpolate(Step):
    def __init__(self, *, template, field_name=None):
        self.__template = template
        self.__field_name = field_name

    def transform_resource(self, source, target):
        if not self.__field_name:
            target.data = source.to_petl().interpolateall(self.__template)
        else:
            target.data = source.to_petl().interpolate(self.__field_name, self.__template)


# TODO: accept WHERE/PREDICAT clause
class cell_replace(Step):
    def __init__(self, *, pattern, replace, field_name=None):
        self.__pattern = pattern
        self.__replace = replace
        self.__field_name = field_name

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


class cell_set(Step):
    def __init__(self, *, field_name=None, value=None):
        self.__field_name = field_name
        self.__value = value

    def transform_resource(self, source, target):
        target.data = source.to_petl().update(self.__field_name, self.__value)
