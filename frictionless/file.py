import os
import glob
from pathlib import Path
from .helpers import cached_property
from . import helpers
from . import config


class File:
    """File representation"""

    def __init__(self, source, *, basepath="", innerpath=None, allow_reading=False):

        # Handle pathlib
        if isinstance(source, Path):
            source = str(source)

        # Set attributes
        self.__source = source
        self.__basepath = basepath
        self.__innerpath = innerpath
        self.__allow_reading = allow_reading

        # Detect attributes
        self.__detect()

    @cached_property
    def path(self):
        return self.__path

    @cached_property
    def data(self):
        return self.__data

    # TODO: review possible values
    @cached_property
    def type(self):
        return self.__type

    @cached_property
    def name(self):
        return self.__name

    @cached_property
    def scheme(self):
        return self.__scheme

    @cached_property
    def format(self):
        return self.__format

    @cached_property
    def innerpath(self):
        return self.__innerpath

    @cached_property
    def compression(self):
        return self.__compression

    @cached_property
    def memory(self):
        return self.__memory

    @cached_property
    def remote(self):
        return self.__remote

    @cached_property
    def multipart(self):
        return self.__multipart

    @cached_property
    def expandable(self):
        return self.__expandable

    @cached_property
    def basepath(self):
        return self.__basepath

    @cached_property
    def normpath(self):
        return self.__normpath

    @cached_property
    def fullpath(self):
        return self.__fullpath

    # Detect

    def __detect(self):
        source = self.__source

        # Detect path/data
        path = None
        data = source
        if isinstance(source, str):
            path = source
            data = None
        elif isinstance(source, list) and source and isinstance(source[0], str):
            path = source
            data = None

        # Detect memory/remote/expandable/multipart
        memory = path is None
        remote = helpers.is_remote_path(self.__basepath or path)
        expandable = not memory and helpers.is_expandable_path(path, self.__basepath)
        multipart = not memory and (isinstance(path, list) or expandable)

        # Detect fullpath
        normpath = path
        fullpath = path
        if not memory:
            if expandable:
                normpath = []
                fullpath = []
                pattern = os.path.join(self.__basepath, path)
                pattern = f"{pattern}/*" if os.path.isdir(pattern) else pattern
                options = {"recursive": True} if "**" in pattern else {}
                for part in sorted(glob.glob(pattern, **options)):
                    normpath.append(os.path.relpath(part, self.__basepath))
                    fullpath.append(os.path.relpath(part, ""))
                if not fullpath:
                    expandable = False
                    multipart = False
                    fullpath = path
            elif multipart:
                fullpath = []
                for part in path:
                    if not helpers.is_remote_path(part):
                        part = os.path.join(self.__basepath, part)
                    fullpath.append(part)
            else:  # for string paths
                if not helpers.is_remote_path(path):
                    fullpath = os.path.join(self.__basepath, path)

        # Detect name
        name = "memory"
        if not memory:
            names = []
            # Path can have a text scheme like "text://row1\nrow2"
            for part in fullpath if multipart else [fullpath.split("\n")[0]]:
                name = os.path.splitext(os.path.basename(part))[0]
                names.append(name)
            name = os.path.commonprefix(names)
            name = helpers.slugify(name, regex_pattern=r"[^-a-z0-9._/]")

        # Detect type
        type = "table"
        if not multipart:
            if memory and isinstance(data, dict):
                type = "resource"
                if data.get("fields") is not None:
                    type = "schema"
                elif data.get("resources") is not None:
                    type = "package"
                elif data.get("tasks") is not None:
                    type = "inquiry"
                elif data.get("steps") is not None:
                    type = "pipeline"
            elif not memory and path.endswith((".json", ".yaml")):
                type = "resource"
                if path.endswith(("schema.json", "schema.yaml")):
                    type = "schema"
                elif path.endswith(("package.json", "package.yaml")):
                    type = "package"
                elif path.endswith(("inquiry.json", "inquiry.yaml")):
                    type = "inquiry"
                elif path.endswith(("pipeline.json", "pipeline.yaml")):
                    type = "pipeline"
                elif self.__allow_reading:
                    # TODO: implement
                    pass

        # Detect scheme/format/innerpath/compression
        scheme = ""
        format = ""
        compression = ""
        innerpath = ""
        detection_path = fullpath[0] if multipart else fullpath
        if not memory:
            scheme, format = helpers.detect_scheme_and_format(detection_path)
            if format in config.COMPRESSION_FORMATS:
                if not multipart:
                    compression = format
                detection_path = detection_path[: -len(format) - 1]
                if self.__innerpath:
                    detection_path = os.path.join(detection_path, self.__innerpath)
                scheme, format = helpers.detect_scheme_and_format(detection_path)
                if format:
                    name = os.path.splitext(name)[0]

        # Set attributes
        self.__path = path
        self.__data = data
        self.__name = name
        self.__type = type
        self.__scheme = scheme
        self.__format = format
        self.__innerpath = innerpath
        self.__compression = compression
        self.__memory = memory
        self.__remote = remote
        self.__multipart = multipart
        self.__expandable = expandable
        self.__normpath = normpath
        self.__fullpath = fullpath
