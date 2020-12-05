import os
import re
from urllib.parse import urlparse, parse_qs
from . import helpers
from . import config


# TODO: Normalize detection functions; merge with Resource?
class Location:
    def __init__(self, resource):

        # Detect source
        source = []
        if resource.data is not None:
            source = resource.data
        elif isinstance(resource.path, str):
            source = resource.path
            if not helpers.is_remote_path(source):
                source = os.path.join(resource.basepath, resource.path)
        elif isinstance(resource.path, list):
            source = []
            for path in resource.path:
                if not helpers.is_remote_path(path):
                    path = os.path.join(resource.basepath, path)
                source.append(path)
        elif resource.path:
            source = resource.path

        # Detect scheme/format/compression/compression_path
        name = helpers.detect_name(source)
        detect = detect_source_scheme_and_format(source)
        compression = config.DEFAULT_COMPRESSION
        compression_path = config.DEFAULT_COMPRESSION_PATH
        if detect[1] in config.COMPRESSION_FORMATS:
            if isinstance(source, list):
                newsource = []
                for path in source:
                    newsource.append(path[: -len(detect[1]) - 1])
                detect = detect_source_scheme_and_format(newsource)
            else:
                compression = detect[1]
                newsource = source[: -len(detect[1]) - 1]
                if resource.get("compressionPath"):
                    newsource = os.path.join(newsource, resource.get("compressionPath"))
                detect = detect_source_scheme_and_format(newsource)
        # TODO: review; do we need defaults?
        scheme = detect[0] or config.DEFAULT_SCHEME
        # TODO: review; do we need defaults?
        format = detect[1] or config.DEFAULT_FORMAT
        if scheme == "text" and source.endswith(f".{format}"):
            source = source[: -(len(format) + 1)]

        # Set attributes
        self.__name = name
        self.__source = source
        self.__scheme = scheme
        self.__format = format
        self.__compression = compression
        self.__compression_path = compression_path

    @property
    def source(self):
        return self.__source

    @property
    def name(self):
        return self.__name

    @property
    def scheme(self):
        return self.__scheme

    @property
    def format(self):
        return self.__format

    @property
    def compression(self):
        return self.__compression

    @property
    def compression_path(self):
        return self.__compression_path

    @property
    def inline(self):
        # TODO: rebase on self.__format == 'inline'
        if self.multipart:
            return False
        return not isinstance(self.source, str)

    @property
    def multipart(self):
        # TODO: rebase on self.__scheme == 'multipart'
        return (
            isinstance(self.source, list)
            and self.source
            and isinstance(self.source[0], str)
        )

    @property
    def remote(self):
        if self.inline:
            return False
        return helpers.is_remote_path(self.source)


# Internal


# TODO: move to Location/plugins
def detect_source_scheme_and_format(source):
    if isinstance(source, list) and source and isinstance(source[0], str):
        scheme, format = detect_source_scheme_and_format(source[0])
        return ("multipart", format)
    if hasattr(source, "read"):
        return ("filelike", None)
    if not isinstance(source, str):
        return (None, "inline")
    if "docs.google.com/spreadsheets" in source:
        if "export" not in source and "pub" not in source:
            return (None, "gsheet")
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
