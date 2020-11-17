import io
import re
import os
import csv
import atexit
import shutil
import zipfile
import chardet
import tempfile
import datetime
import stringcase
from inspect import signature
from importlib import import_module
from urllib.parse import urlparse, parse_qs
from _thread import RLock  # type: ignore
from . import config


# General


def apply_function(function, descriptor):
    options = create_options(descriptor)
    return function(**options)


def create_options(descriptor):
    return {stringcase.snakecase(key): value for key, value in descriptor.items()}


def create_descriptor(**options):
    return {stringcase.camelcase(key): value for key, value in options.items()}


def stringify_header(cells):
    return ["" if cell is None else str(cell).strip() for cell in cells]


def get_name(value):
    return getattr(value, "__name__", value.__class__.__name__)


def pass_through(iterator):
    for item in iterator:
        pass


def remove_non_values(mapping):
    return {key: value for key, value in mapping.items() if value is not None}


def rows_to_data(rows):
    if not rows:
        return []
    return [list(rows[0].schema.field_names)] + [row.to_list() for row in rows]


def parse_csv_string(string, *, convert=str, fallback=False):
    if string is None:
        return None
    reader = csv.reader(io.StringIO(string), delimiter=",")
    result = []
    for row in reader:
        for cell in row:
            try:
                cell = convert(cell)
            except ValueError:
                if not fallback:
                    raise
                pass
            result.append(cell)
        return result


def stringify_csv_string(cells):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(cells)
    result = stream.getvalue().rstrip("\r\n")
    return result


def deepfork(value):
    if isinstance(value, dict):
        value = {key: deepfork(value) for key, value in value.items()}
    elif isinstance(value, list):
        value = [deepfork(value) for value in value]
    elif isinstance(value, set):
        value = {deepfork(value) for value in value}
    return value


def deepsafe(value):
    if isinstance(value, dict):
        value = {key: deepsafe(value) for key, value in value.items()}
    elif isinstance(value, list):
        value = [deepsafe(value) for value in value]
    elif isinstance(value, set):
        value = {deepsafe(value) for value in value}
    elif isinstance(value, io.BufferedRandom):
        value = "inline"
    return value


def import_from_plugin(name, *, plugin):
    try:
        return import_module(name)
    except ImportError:
        exceptions = import_module("frictionless.exceptions")
        errors = import_module("frictionless.errors")
        error = errors.Error(note=f'Please install "frictionless[{plugin}]"')
        raise exceptions.FrictionlessException(error)


def copy_merge(source, patch):
    source = (source or {}).copy()
    source.update(patch)
    return source


def filter_cells(cells, field_positions):
    result = []
    for field_position, cell in enumerate(cells, start=1):
        if field_position in field_positions:
            result.append(cell)
    return result


def compile_regex(items):
    if items is not None:
        result = []
        for item in items:
            if isinstance(item, str) and item.startswith("<regex>"):
                item = re.compile(item.replace("<regex>", ""))
            result.append(item)
        return result


def detect_name(source):
    if isinstance(source, str) and "\n" not in source:
        return os.path.splitext(os.path.basename(source))[0]
    if isinstance(source, list) and source and isinstance(source[0], str):
        return os.path.splitext(os.path.basename(source[0]))[0]
    return "memory"


def detect_basepath(descriptor):
    basepath = ""
    if isinstance(descriptor, str):
        basepath = os.path.dirname(descriptor)
        if basepath and not is_remote_path(basepath):
            basepath = os.path.relpath(basepath, start=os.getcwd())
    return basepath


def ensure_dir(path):
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)


def move_file(source, target):
    ensure_dir(target)
    shutil.move(source, target)


def copy_file(source, target):
    if isinstance(source, (tuple, list)):
        source = os.path.join(*source)
    if isinstance(target, (tuple, list)):
        target = os.path.join(*target)
    ensure_dir(target)
    shutil.copy(source, target)


def create_byte_stream(bytes):
    stream = io.BufferedRandom(io.BytesIO())
    stream.write(bytes)
    stream.seek(0)
    return stream


def is_remote_path(path):
    return urlparse(path).scheme in config.REMOTE_SCHEMES


def is_safe_path(path):
    contains_windows_var = lambda val: re.match(r"%.+%", val)
    contains_posix_var = lambda val: re.match(r"\$.+", val)
    unsafeness_conditions = [
        os.path.isabs(path),
        ("..%s" % os.path.sep) in path,
        path.startswith("~"),
        os.path.expandvars(path) != path,
        contains_windows_var(path),
        contains_posix_var(path),
    ]
    return not any(unsafeness_conditions)


def is_zip_descriptor(descriptor):
    if isinstance(descriptor, str):
        parsed = urlparse(descriptor)
        format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower()
        return format == "zip"


def is_only_strings(cells):
    for cell in cells:
        if cell is None:
            continue
        if not isinstance(cell, str):
            return False
        try:
            float(cell)
            return False
        except Exception:
            pass
    return True


def unzip_descriptor(descriptor, compression_path):
    frictionless = import_module("frictionless")
    file = frictionless.File(descriptor, compression="no")
    with frictionless.system.create_loader(file) as loader:
        byte_stream = loader.byte_stream
        if loader.remote:
            byte_stream = tempfile.TemporaryFile()
            shutil.copyfileobj(loader.byte_stream, byte_stream)
            byte_stream.seek(0)
        with zipfile.ZipFile(byte_stream, "r") as zip:
            tempdir = tempfile.mkdtemp()
            zip.extractall(tempdir)
            atexit.register(shutil.rmtree, tempdir)
            descriptor = os.path.join(tempdir, compression_path)
    return descriptor


def parse_resource_hash(hash):
    if not hash:
        return (config.DEFAULT_HASHING, "")
    parts = hash.split(":", maxsplit=1)
    if len(parts) == 1:
        return (config.DEFAULT_HASHING, parts[0])
    return parts


def detect_encoding(sample):
    result = chardet.detect(sample)
    confidence = result["confidence"] or 0
    encoding = result["encoding"] or config.DEFAULT_ENCODING
    if confidence < config.DEFAULT_INFER_ENCODING_CONFIDENCE:
        encoding = config.DEFAULT_ENCODING
    if encoding == "ascii":
        encoding = config.DEFAULT_ENCODING
    return encoding


def detect_source_type(source):
    source_type = "table"
    if isinstance(source, dict):
        if source.get("fields") is not None:
            source_type = "schema"
        if source.get("path") is not None or source.get("data") is not None:
            source_type = "resource"
        if source.get("resources") is not None:
            source_type = "package"
        if source.get("tasks") is not None:
            source_type = "inquiry"
    if isinstance(source, str):
        if source.endswith("schema.json") or source.endswith("schema.yaml"):
            source_type = "schema"
        if source.endswith("resource.json") or source.endswith("resource.yaml"):
            source_type = "resource"
        if source.endswith("package.json") or source.endswith("package.yaml"):
            source_type = "package"
        if source.endswith("inquiry.json") or source.endswith("inquiry.yaml"):
            source_type = "inquiry"
    return source_type


# TODO: move to Location/plugins
def detect_source_scheme_and_format(source):
    if hasattr(source, "read"):
        return ("stream", None)
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


# Collections


class ControlledDict(dict):
    def __onchange__(self, onchange=None):
        if onchange is not None:
            self.__onchange = onchange
            return
        onchange = getattr(self, "_ControlledDict__onchange", None)
        if onchange:
            onchange(self) if signature(onchange).parameters else onchange()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.__onchange__()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.__onchange__()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.__onchange__()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.__onchange__()
        return result

    def popitem(self, *args, **kwargs):
        result = super().popitem(*args, **kwargs)
        self.__onchange__()
        return result

    def setdefault(self, *args, **kwargs):
        result = super().setdefault(*args, **kwargs)
        self.__onchange__()
        return result

    def update(self, *args, **kwargs):
        result = super().update(*args, **kwargs)
        self.__onchange__()
        return result


class ControlledList(list):
    def __onchange__(self, onchange=None):
        if onchange is not None:
            self.__onchange = onchange
            return
        onchange = getattr(self, "_ControlledList__onchange", None)
        if onchange:
            onchange(self) if signature(onchange).parameters else onchange()

    def __setitem__(self, *args, **kwargs):
        result = super().__setitem__(*args, **kwargs)
        self.__onchange__()
        return result

    def __delitem__(self, *args, **kwargs):
        result = super().__delitem__(*args, **kwargs)
        self.__onchange__()
        return result

    def append(self, *args, **kwargs):
        result = super().append(*args, **kwargs)
        self.__onchange__()
        return result

    def clear(self, *args, **kwargs):
        result = super().clear(*args, **kwargs)
        self.__onchange__()
        return result

    def extend(self, *args, **kwargs):
        result = super().extend(*args, **kwargs)
        self.__onchange__()
        return result

    def insert(self, *args, **kwargs):
        result = super().insert(*args, **kwargs)
        self.__onchange__()
        return result

    def pop(self, *args, **kwargs):
        result = super().pop(*args, **kwargs)
        self.__onchange__()
        return result

    def remove(self, *args, **kwargs):
        result = super().remove(*args, **kwargs)
        self.__onchange__()
        return result


# Measurements


class Timer:
    def __init__(self):
        self.__start = datetime.datetime.now()
        self.__stop = None

    @property
    def time(self):
        if not self.__stop:
            self.__stop = datetime.datetime.now()
        return round((self.__stop - self.__start).total_seconds(), 3)


def get_current_memory_usage():
    # Current memory usage of the current process in MB
    # This will only work on systems with a /proc file system (like Linux)
    # https://stackoverflow.com/questions/897941/python-equivalent-of-phps-memory-get-usage
    try:
        with open("/proc/self/status") as status:
            for line in status:
                parts = line.split()
                key = parts[0][2:-1].lower()
                if key == "rss":
                    return int(parts[1]) / 1000
    except Exception:
        pass


# Backports


# NOTE: Can be removed for Python3.8+
class cached_property:
    def __init__(self, func):
        self.func = func
        self.attrname = None
        self.__doc__ = func.__doc__
        self.lock = RLock()

    def __set_name__(self, owner, name):
        if self.attrname is None:
            self.attrname = name
        elif name != self.attrname:
            raise TypeError(
                "Cannot assign the same cached_property to two different names "
                f"({self.attrname!r} and {name!r})."
            )

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.attrname is None:
            raise TypeError(
                "Cannot use cached_property instance without calling __set_name__ on it."
            )
        try:
            cache = instance.__dict__
        except AttributeError:  # not all objects have __dict__ (e.g. class defines slots)
            msg = (
                f"No '__dict__' attribute on {type(instance).__name__!r} "
                f"instance to cache {self.attrname!r} property."
            )
            raise TypeError(msg) from None
        val = cache.get(self.attrname, config.UNDEFINED)
        if val is config.UNDEFINED:
            with self.lock:
                # check if another thread filled cache while we awaited lock
                val = cache.get(self.attrname, config.UNDEFINED)
                if val is config.UNDEFINED:
                    val = self.func(instance)
                    try:
                        cache[self.attrname] = val
                    except TypeError:
                        msg = (
                            f"The '__dict__' attribute on {type(instance).__name__!r} instance "
                            f"does not support item assignment for caching {self.attrname!r} property."
                        )
                        raise TypeError(msg) from None
        return val
