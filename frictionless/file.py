import os
import re
import glob
from urllib.parse import urlparse, parse_qs
from .helpers import cached_property
from . import helpers
from . import config


# TODO: export in __init__.py
# TODO: rename module to file.py
class File:
    def __init__(
        self,
        source,
        *,
        basepath="",
        compression_path=None,
        allow_contents_reading=False,
    ):

        # Set attributes
        self.__source = source
        self.__basepath = basepath
        self.__compression_path = compression_path
        self.__allow_contents_reading = allow_contents_reading

        # Detect attributes
        self.__detect()

    @cached_property
    def path(self):
        return self.__path

    @cached_property
    def data(self):
        return self.__data

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
    def compression(self):
        return self.__compression

    @cached_property
    def compression_path(self):
        return self.__compression_path

    @cached_property
    def inline(self):
        return self.__inline

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

        # Detect inline/remote/expandable/multipart
        inline = path is None
        remote = helpers.is_remote_path(self.__basepath or path)
        expandable = not inline and helpers.is_expandable(path, self.__basepath)
        multipart = not inline and (isinstance(path, list) or expandable)

        # Detect fullpath
        fullpath = path
        if not inline:
            if expandable:
                fullpath = []
                pattern = os.path.join(self.__basepath, path)
                pattern = f"{pattern}/*" if os.path.isdir(pattern) else pattern
                options = {"recursive": True} if "**" in pattern else {}
                for part in sorted(glob.glob(pattern, **options)):
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
        name = "inline"
        if not inline:
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
            if inline and isinstance(data, dict):
                type = "resource"
                if data.get("fields") is not None:
                    type = "schema"
                elif data.get("resources") is not None:
                    type = "package"
            elif not inline and path.endswith((".json", ".yaml")):
                type = "resource"
                if path.endswith(("schema.json", "schema.yaml")):
                    type = "schema"
                elif path.endswith(("package.json", "package.yaml")):
                    type = "package"
                elif self.__allow_contents_reading:
                    # TODO: implement
                    pass

        # Detect scheme/format/compression/compression_path
        scheme = ""
        # TODO: move to inline plugin?
        format = "inline"
        compression = "no"
        compression_path = ""
        detection_path = fullpath[0] if multipart else fullpath
        if not inline:
            scheme, format = self.__detect_scheme_and_format(detection_path)
            if format in config.COMPRESSION_FORMATS:
                if not multipart:
                    compression = format
                detection_path = detection_path[: -len(format) - 1]
                if self.__compression_path:
                    detection_path = os.path.join(detection_path, self.__compression_path)
                scheme, format = self.__detect_scheme_and_format(detection_path)

        # TODO: move to filelike plugin?
        if hasattr(data, "read"):
            scheme = "filelike"
            format = ""

        # TODO: move to multipart plugin?
        if multipart:
            scheme = "multipart"

        # Set attributes
        self.__path = path
        self.__data = data
        self.__name = name
        self.__type = type
        self.__scheme = scheme
        self.__format = format
        self.__compression = compression
        self.__compression_path = compression_path
        self.__inline = inline
        self.__remote = remote
        self.__multipart = multipart
        self.__expandable = expandable
        self.__fullpath = fullpath

    # TODO: move to helpers when it's only url parsing
    def __detect_scheme_and_format(self, source):
        # TODO: move to gsheets plugin
        if "docs.google.com/spreadsheets" in source:
            if "export" not in source and "pub" not in source:
                return ("", "gsheets")
            elif "csv" in source:
                return ("https", "csv")
        # TODO: move to sql plugin
        # Fix for sources like: db2+ibm_db://username:password@host:port/database
        if re.search(r"\+.*://", source):
            scheme, source = source.split("://", maxsplit=1)
            parsed = urlparse(f"//{source}", scheme=scheme)
        else:
            parsed = urlparse(source)
        scheme = parsed.scheme.lower()
        if len(scheme) < 2:
            scheme = config.DEFAULT_SCHEME
        format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower() or None
        if format is None:
            # Test if query string contains a "format=" parameter.
            query_string = parse_qs(parsed.query)
            query_string_format = query_string.get("format")
            if query_string_format is not None and len(query_string_format) == 1:
                format = query_string_format[0]
        return (scheme or "", format or "")
