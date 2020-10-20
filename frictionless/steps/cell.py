from ..step import Step
from ..helpers import ResourceView


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
