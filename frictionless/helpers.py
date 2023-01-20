from __future__ import annotations
import io
import re
import os
import csv
import ast
import json
import glob
import shutil
import inspect
import tempfile
import datetime
import textwrap
import stringcase
from copy import deepcopy
from collections.abc import Mapping
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs
from typing import Union, Any, Optional
from .platform import platform


# General


def compact(text):
    return " ".join(filter(None, textwrap.dedent(text).splitlines()))


def apply_function(function, descriptor):
    options = create_options(descriptor)
    return function(**options)


def create_options(descriptor):
    return {stringcase.snakecase(key): value for key, value in descriptor.items()}


def create_descriptor(**options):
    return {stringcase.camelcase(key): value for key, value in options.items()}


def remove_default(descriptor, key, default):
    if descriptor.get(key) == default:
        descriptor.pop(key)


def stringify_label(cells):
    return ["" if cell is None else str(cell).strip() for cell in cells]


def get_name(value):
    return getattr(value, "__name__", value.__class__.__name__)


def pass_through(iterator):
    for _ in iterator:
        pass


def safe_format(text, data):
    return text.format_map(SafeFormatDict(data))


class SafeFormatDict(dict):
    def __missing__(self, key):
        return ""


def cleaned_dict(**options):
    return dict(**remove_non_values(options))


def remove_non_values(mapping):
    return {key: value for key, value in mapping.items() if value is not None}


def rows_to_data(rows):
    if not rows:
        return []
    data = []
    data.append(list(rows[0].field_names))
    for row in rows:
        data.append([cell if cell is not None else "" for cell in row.to_list()])
    return data


def is_class_accept_option(cls, name):
    sig = inspect.signature(cls.__init__)
    return name in sig.parameters


@contextmanager
def ensure_open(thing):
    if not thing.closed:
        yield thing
    else:
        try:
            thing.open()
            yield thing
        finally:
            thing.close()


def read_file(path, mode="r"):
    with open(path, mode) as file:
        return file.read()


def copy_merge(source, patch={}, **kwargs):
    source = (source or {}).copy()
    source.update(patch)
    source.update(kwargs)
    return source


def compile_regex(items):
    if items is not None:
        result = []
        for item in items:
            if isinstance(item, str) and item.startswith("<regex>"):
                item = re.compile(item.replace("<regex>", ""))
            result.append(item)
        return result


def parse_basepath(descriptor):
    basepath = ""
    if isinstance(descriptor, str):
        basepath = os.path.dirname(descriptor)
        if basepath and not is_remote_path(basepath):
            if not os.path.abspath(basepath):
                basepath = os.path.relpath(basepath, start=os.getcwd())
    return basepath


def join_basepath(path: str, basepath: Optional[str] = None):
    if not basepath:
        return path
    if is_remote_path(path):
        return path
    return os.path.join(basepath, path)


def parse_scheme_and_format(path: str):
    parsed = urlparse(path)
    if re.search(r"\+.*://", path):
        # For sources like: db2+ibm_db://username:password@host:port/database
        scheme, path = path.split("://", maxsplit=1)
        parsed = urlparse(f"//{path}", scheme=scheme)
    scheme = parsed.scheme.lower()
    if len(scheme) < 2:
        scheme = "file"
    format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower()
    if not format:
        # Test if query string contains a "format=" parameter.
        query_string = parse_qs(parsed.query)
        query_string_format = query_string.get("format")
        if query_string_format is not None and len(query_string_format) == 1:
            format = query_string_format[0]
    return scheme, format


def merge_jsonschema(base, head):
    result = deepcopy(base)
    base_required = base.get("required", [])
    head_required = head.get("required", [])
    if base_required or head_required:
        result["required"] = list(set(base_required + head_required))
    result["properties"] = copy_merge(
        base.get("properties", {}),
        head.get("properties", {}),
    )
    return result


def ensure_dir(path):
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath)


def move_file(source: str, target: str):
    ensure_dir(target)
    shutil.move(source, target)


def copy_file(source: str, target: str):
    if isinstance(source, (tuple, list)):
        source = os.path.join(*source)
    if isinstance(target, (tuple, list)):
        target = os.path.join(*target)
    ensure_dir(target)
    shutil.copy(source, target)


def copy_folder(source: str, target: str):
    ensure_dir(target)
    shutil.copytree(source, target)


def write_file(path: str, body: Any, *, mode: str = "wt"):
    encoding = "utf-8" if mode == "wt" else None
    with tempfile.NamedTemporaryFile(mode, delete=False, encoding=encoding) as file:
        file.write(body)
        file.flush()
    move_file(file.name, path)
    os.chmod(path, 0o644)


def create_byte_stream(bytes):
    stream = io.BufferedRandom(io.BytesIO())  # type: ignore
    stream.write(bytes)
    stream.seek(0)
    return stream


def is_remote_path(path):
    path = path[0] if path and isinstance(path, list) else path
    scheme = urlparse(path).scheme
    if not scheme:
        return False
    if path.lower().startswith(f"{scheme}:\\"):
        return False
    return True


def normalize_path(path: str, *, basepath: Optional[str] = None):
    if not is_remote_path(path) and not os.path.isabs(path):
        if basepath:
            separator = os.path.sep
            if is_remote_path(basepath):
                separator = "/"
            path = separator.join([basepath, path])
    return path


# NOTE:
# We need to rebase this function on checking actual path
# being withing a basepath directory (it's a safer approach)
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


def is_directory_source(source: Any):
    if not isinstance(source, str):
        return False
    if is_remote_path(source):
        return False
    if not os.path.isdir(source):
        return False
    return True


def is_expandable_source(source: Any):
    if isinstance(source, list):
        if len(source) == len(list(filter(lambda path: isinstance(path, str), source))):
            return True
    if not isinstance(source, str):
        return False
    if is_remote_path(source):
        return False
    return glob.has_magic(source) or os.path.isdir(source)


def expand_source(source: Union[list, str], *, basepath: Optional[str] = None):
    if isinstance(source, list):
        return source
    paths = []
    if basepath:
        source = os.path.join(basepath, source)
    pattern = f"{source}/*" if os.path.isdir(source) else source
    configs = {"recursive": True} if "**" in pattern else {}
    for path in sorted(glob.glob(pattern, **configs)):
        if basepath:
            path = os.path.relpath(path, basepath)
        paths.append(path)
    return paths


def is_zip_descriptor(descriptor):
    if isinstance(descriptor, str):
        parsed = urlparse(descriptor)
        format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower()
        return format == "zip"


def is_descriptor_source(source):
    if isinstance(source, Mapping):
        return True
    if isinstance(source, str):
        if source.endswith((".json", ".yaml")):
            return True
    return False


def is_type(object, name):
    return type(object).__name__ == name


def parse_json_string(string):
    if string is None:
        return None
    if string.startswith("{") and string.endswith("}"):
        return json.loads(string)
    return string


def parse_descriptors_string(string):
    if string is None:
        return None
    descriptors = []
    parts = string.split(" ")
    for part in parts:
        type, *props = part.split(":")
        descriptor = dict(type=type)
        for prop in props:
            name, value = prop.split("=")
            try:
                value = ast.literal_eval(value)
            except Exception:
                pass
            descriptor[name] = value
        descriptors.append(descriptor)
    return descriptors


def parse_csv_string(string, *, convert: type = str, fallback=False):
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


def stringify_csv_string(cells, **options):
    stream = io.StringIO()
    writer = csv.writer(stream, **options)
    writer.writerow(cells)
    result = stream.getvalue().rstrip("\r\n")
    return result


def parse_resource_hash_v1(hash):
    parts = hash.split(":", maxsplit=1)
    if len(parts) == 1:
        return ("md5", parts[0])
    return parts


class Timer:
    def __init__(self):
        self.__start = datetime.datetime.now()
        self.__stop = None

    @property
    def time(self):
        if not self.__stop:
            self.__stop = datetime.datetime.now()
        return round((self.__stop - self.__start).total_seconds(), 3)


def slugify(text, **options):
    """There is a conflict between python-slugify and awesome-slugify
    So we import from a proper module manually
    """

    # Import
    from slugify.slugify import slugify

    # Slugify
    slug = slugify(text, **options)
    return slug


def get_current_memory_usage():
    """Current memory usage of the current process in MB
    This will only work on systems with a /proc file system (like Linux)
    https://stackoverflow.com/questions/897941/python-equivalent-of-phps-memory-get-usage
    """
    try:
        with open("/proc/self/status") as status:
            for line in status:
                parts = line.split()
                key = parts[0][2:-1].lower()
                if key == "rss":
                    return int(parts[1]) / 1000
    except Exception:
        pass


def create_yaml_dumper():
    class IndentDumper(platform.yaml.SafeDumper):
        def increase_indent(self, flow=False, indentless=False):
            return super().increase_indent(flow, False)

    return IndentDumper
