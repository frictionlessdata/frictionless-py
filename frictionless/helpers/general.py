from __future__ import annotations

import ast
import csv
import datetime
import glob
import io
import json
import os
import re
import shutil
import tempfile
from collections.abc import Mapping
from contextlib import contextmanager
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple, Type, TypeVar, Union
from urllib.parse import parse_qs, urlparse

from ..vendors import stringcase # type: ignore

# General


def create_options(descriptor: Dict[str, Any]) -> Dict[str, Any]:
    return {stringcase.snakecase(key): value for key, value in descriptor.items()}  # type: ignore


def create_descriptor(**options: Any) -> Dict[str, Any]:
    return {stringcase.camelcase(key): value for key, value in options.items()}  # type: ignore


def stringify_label(cells: List[Any]):
    return ["" if cell is None else str(cell).strip() for cell in cells]


def get_name(value: Any):
    return getattr(value, "__name__", value.__class__.__name__)


def pass_through(iterator: Iterator[Any]):
    for _ in iterator:
        pass


def safe_format(text: str, data: Dict[str, Any]):
    return text.format_map(SafeFormatDict(data))


class SafeFormatDict(Dict[str, Any]):
    def __missing__(self, key: str):
        return ""


def to_json(obj: Any, *, encoder_class: Optional[Any] = None) -> str:
    return json.dumps(
        obj,
        indent=2,
        ensure_ascii=False,
        cls=encoder_class,
    )


def to_yaml(obj: Any) -> str:
    from ..platform import platform

    return platform.yaml.dump(
        obj,
        sort_keys=False,
        allow_unicode=True,
        Dumper=create_yaml_dumper(),
    )


def cleaned_dict(**options: Any) -> Dict[str, Any]:
    return dict(**remove_non_values(options))


def remove_non_values(mapping: Dict[str, Any]):
    return {key: value for key, value in mapping.items() if value is not None}


def normalize_source(source: Any) -> Any:
    if isinstance(source, Path):
        source = str(source)
    if isinstance(source, Mapping):
        source = {key: value for key, value in source.items()}  # type: ignore
    return source


@contextmanager
def ensure_open(thing: Any):
    if not thing.closed:
        yield thing
    else:
        try:
            thing.open()
            yield thing
        finally:
            thing.close()


def copy_merge(source: Dict[str, Any], patch: Dict[str, Any] = {}, **kwargs: Any):
    source = (source or {}).copy()
    source.update(patch)
    source.update(kwargs)
    return source


def parse_basepath(descriptor: Union[str, Dict[str, Any]]):
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
    if is_remote_path(basepath):
        return f"{basepath}/{path}"
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


def merge_jsonschema(base: Dict[str, Any], head: Dict[str, Any]):
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


def ensure_dir(path: str) -> None:
    if not os.path.isdir(path):
        path = os.path.dirname(path)
    if path and not os.path.exists(path):
        os.makedirs(path)


def move_file(source: str, target: str) -> str:
    ensure_dir(target)
    return shutil.move(source, target)


def read_file(path: str, mode: str = "r"):
    with open(path, mode) as file:
        return file.read()


def write_file(path: str, body: Any, *, mode: str = "wt"):
    encoding = "utf-8" if mode == "wt" else None
    with tempfile.NamedTemporaryFile(mode, delete=False, encoding=encoding) as file:
        file.write(body)
        file.flush()
    move_file(file.name, path)
    os.chmod(path, 0o644)


def is_remote_path(path: str) -> bool:
    path = path[0] if path and isinstance(path, list) else path
    scheme = urlparse(path).scheme
    if not scheme:
        return False
    if path.lower().startswith(scheme + ":\\"):
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
# being within a basepath directory (it's a safer approach)
def is_safe_path(path: str):
    contains_windows_var = lambda val: re.match(r"%.+%", val)  # type: ignore
    contains_posix_var = lambda val: re.match(r"\$.+", val)  # type: ignore
    unsafeness_conditions = [
        os.path.isabs(path),
        ("..%s" % os.path.sep) in path,
        path.startswith("~"),
        os.path.expandvars(path) != path,
        contains_windows_var(path),
        contains_posix_var(path),
    ]
    return not any(unsafeness_conditions)


def is_directory_source(source: Any) -> bool:
    if not isinstance(source, str):
        return False
    if is_remote_path(source):
        return False
    if not os.path.isdir(source):
        return False
    return True


def is_expandable_source(source: Any) -> bool:
    if isinstance(source, list):
        if len(source) == len(list(filter(lambda path: isinstance(path, str), source))):  # type: ignore
            return True
    if not isinstance(source, str):
        return False
    if is_remote_path(source):
        return False
    return glob.has_magic(source) or os.path.isdir(source)


def expand_source(source: Union[List[Any], str], *, basepath: Optional[str] = None):
    if isinstance(source, list):
        return source
    paths: List[str] = []
    if basepath:
        source = os.path.join(basepath, source)
    pattern = f"{source}/*" if os.path.isdir(source) else source
    configs = {"recursive": True} if "**" in pattern else {}
    for path in sorted(glob.glob(pattern, **configs)):  # type: ignore
        if basepath:
            path = os.path.relpath(path, basepath)
        paths.append(path)
    return paths


def is_zip_descriptor(descriptor: Union[str, Dict[str, Any]]):
    if isinstance(descriptor, str):
        parsed = urlparse(descriptor)
        format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower()
        return format == "zip"


def is_type(object: type, name: str):
    return type(object).__name__ == name


def parse_json_string(string: Optional[str]):
    if string is None:
        return None
    if string.startswith("{") and string.endswith("}"):
        return json.loads(string)
    return string


def parse_descriptors_string(string: Optional[str]):
    if string is None:
        return None
    descriptors: List[Dict[str, Any]] = []
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


T = TypeVar("T", int, str)


def parse_csv_string_typed(
    string: str, *, convert: Type[T] = str, fallback: bool = False
) -> List[T]:
    reader = csv.reader(io.StringIO(string), delimiter=",")
    result: List[T] = []
    for row in reader:
        for cell in row:
            try:
                cell = convert(cell)
            except ValueError:
                if not fallback:
                    raise
                pass
            result.append(cell)  # type: ignore
        break
    return result


def stringify_csv_string(cells: List[str], **options: Any):
    stream = io.StringIO()
    writer = csv.writer(stream, **options)
    writer.writerow(cells)
    result = stream.getvalue().rstrip("\r\n")
    return result


def parse_resource_hash_v1(hash: str) -> Tuple[str, str]:
    parts = hash.split(":", maxsplit=1)
    if len(parts) == 1:
        return ("md5", parts[0])
    return parts[0], parts[1]


class Timer:
    def __init__(self):
        self.__start = datetime.datetime.now()
        self.__stop = None

    @property
    def time(self):
        if not self.__stop:
            self.__stop = datetime.datetime.now()
        return round((self.__stop - self.__start).total_seconds(), 3)


def slugify(text: str, **options: Any):
    """There is a conflict between python-slugify and awesome-slugify
    So we import from a proper module manually
    """

    # Import
    from slugify.slugify import slugify

    # Slugify
    slug = slugify(text, **options)
    return slug


def create_yaml_dumper():
    from ..platform import platform

    class IndentDumper(platform.yaml.SafeDumper):
        def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
            return super().increase_indent(flow, False)  # type: ignore

    return IndentDumper
