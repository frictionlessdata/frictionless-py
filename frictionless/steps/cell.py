from ..step import Step
from ..helpers import ResourceView


# TODO: add set_cells?
# TODO: accept WHERE/PREDICAT clause
class replace_cells(Step):
    def __init__(self, *, source, target, name=None):
        self.__source = source
        self.__target = target
        self.__name = name

    def transform_resource(self, source, target):
        if not self.__name:
            target.data = ResourceView(source).replaceall(self.__source, self.__target)
        else:
            target.data = ResourceView(source).replace(
                self.__name, self.__source, self.__target
            )


class fill_cells(Step):
    def __init__(self, *, name=None, value=None, direction=None):
        assert direction in [None, "down", "right", "left"]
        self.__name = name
        self.__value = value
        self.__direction = direction

    def transform_resource(self, source, target):
        if self.__value:
            target.data = ResourceView(source).convert(self.__name, {None: self.__value})
        elif self.__direction == "down":
            if self.__name:
                target.data = ResourceView(source).filldown(self.__name)
            else:
                target.data = ResourceView(source).filldown()
        elif self.__direction == "right":
            target.data = ResourceView(source).fillright()
        elif self.__direction == "left":
            target.data = ResourceView(source).fillleft()


# TODO: accept WHERE/PREDICAT clause
class convert_cells(Step):
    def __init__(self, *, value, name=None):
        self.__value = value
        self.__name = name

    def transform_resource(self, source, target):
        value = self.__value
        if not self.__name:
            if not callable(value):
                value = lambda val: self.__value
            target.data = ResourceView(source).convertall(value)
        else:
            if not callable(value):
                target.data = ResourceView(source).update(self.__name, value)
            else:
                target.data = ResourceView(source).convert(self.__name, value)
