import os
import re
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
        basepath=None,
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
    def source(self):
        return self.__source

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

    # Detect

    def __detect(self):
        source = self.__source

        # Detect path/data
        path = source
        data = None
        if isinstance(source, list) and (source and not isinstance(source[0], str)):
            path = None
            data = source

        # Detect inline/remote/multipart
        inline = path is None
        remote = helpers.is_remote_path(self.__basepath or path)
        multipart = not inline and isinstance(path, list)

        # Detect name
        name = "inline"
        if not inline:
            # Path can have a text scheme like "text://row1\nrow2"
            name = path[0] if multipart else path.split("\n")[0]
            name = os.path.splitext(os.path.basename(name))[0]
            name = helpers.slugify(name, regex_pattern=r"[^-a-z0-9._/]")

        # Detect type
        type = "general"
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
        detect = self.__detect_scheme_and_format(source)
        compression = config.DEFAULT_COMPRESSION
        compression_path = config.DEFAULT_COMPRESSION_PATH
        if detect[1] in config.COMPRESSION_FORMATS:
            if isinstance(source, list):
                newsource = []
                for path in source:
                    newsource.append(path[: -len(detect[1]) - 1])
                detect = self.__detect_scheme_and_format(newsource)
            else:
                compression = detect[1]
                newsource = source[: -len(detect[1]) - 1]
                if self.__compression_path:
                    newsource = os.path.join(newsource, self.__compression_path)
                detect = self.__detect_scheme_and_format(newsource)
        # TODO: review; do we need defaults?
        scheme = detect[0] or config.DEFAULT_SCHEME
        # TODO: review; do we need defaults?
        format = detect[1] or config.DEFAULT_FORMAT
        if scheme == "text" and source.endswith(f".{format}"):
            source = source[: -(len(format) + 1)]

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

    # TODO: move some parts to plugins
    def __detect_scheme_and_format(self, source):
        if isinstance(source, list) and source and isinstance(source[0], str):
            scheme, format = self.__detect_scheme_and_format(source[0])
            return ("multipart", format)
        if hasattr(source, "read"):
            return ("filelike", None)
        if not isinstance(source, str):
            return (None, "inline")
        if "docs.google.com/spreadsheets" in source:
            if "export" not in source and "pub" not in source:
                return (None, "gsheets")
            elif "csv" in source:
                return ("https", "csv")
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
        return (scheme, format)
