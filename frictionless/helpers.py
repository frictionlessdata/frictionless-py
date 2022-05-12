import io
import re
import os
import csv
import json
import glob
import jinja2
import marko
import atexit
import shutil
import zipfile
import tempfile
import datetime
import platform
import textwrap
import stringcase
from typing import List, Union
from inspect import signature
from html.parser import HTMLParser
from importlib import import_module
from contextlib import contextmanager
from urllib.parse import urlparse, parse_qs
from _thread import RLock  # type: ignore
from . import settings


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


def stringify_label(cells):
    return ["" if cell is None else str(cell).strip() for cell in cells]


def get_name(value):
    return getattr(value, "__name__", value.__class__.__name__)


def pass_through(iterator):
    for item in iterator:
        pass


def safe_format(text, data):
    return text.format_map(SafeFormatDict(data))


class SafeFormatDict(dict):
    def __missing__(self, key):
        return ""


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


def import_from_plugin(name, *, plugin):
    try:
        return import_module(name)
    except ImportError:
        module = import_module("frictionless.exception")
        errors = import_module("frictionless.errors")
        error = errors.GeneralError(note=f'Please install "frictionless[{plugin}]"')
        raise module.FrictionlessException(error)


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


def parse_basepath(descriptor):
    basepath = ""
    if isinstance(descriptor, str):
        basepath = os.path.dirname(descriptor)
        if basepath and not is_remote_path(basepath):
            if not os.path.abspath(basepath):
                basepath = os.path.relpath(basepath, start=os.getcwd())
    return basepath


def parse_scheme_and_format(source):
    parsed = urlparse(source)
    if re.search(r"\+.*://", source):
        # For sources like: db2+ibm_db://username:password@host:port/database
        scheme, source = source.split("://", maxsplit=1)
        parsed = urlparse(f"//{source}", scheme=scheme)
    scheme = parsed.scheme.lower()
    if len(scheme) < 2:
        scheme = settings.DEFAULT_SCHEME
    format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower()
    if not format:
        # Test if query string contains a "format=" parameter.
        query_string = parse_qs(parsed.query)
        query_string_format = query_string.get("format")
        if query_string_format is not None and len(query_string_format) == 1:
            format = query_string_format[0]
    return scheme, format


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


def write_file(path, text):
    with tempfile.NamedTemporaryFile("wt", delete=False, encoding="utf-8") as file:
        file.write(text)
        file.flush()
    move_file(file.name, path)
    os.chmod(path, 0o644)


def create_byte_stream(bytes):
    stream = io.BufferedRandom(io.BytesIO())
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


def join_path(basepath, path):
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


def is_expandable_path(path, basepath):
    if not isinstance(path, str):
        return False
    if is_remote_path(path):
        return False
    fullpath = os.path.join(basepath, path)
    return glob.has_magic(fullpath) or os.path.isdir(fullpath)


def is_zip_descriptor(descriptor):
    if isinstance(descriptor, str):
        parsed = urlparse(descriptor)
        format = os.path.splitext(parsed.path or parsed.netloc)[1][1:].lower()
        return format == "zip"


def is_type(object, name):
    return type(object).__name__ == name


def is_platform(name):
    current = platform.system()
    if name == "linux":
        return current == "Linux"
    elif name == "macos":
        return current == "Darwin"
    elif name == "windows":
        return current == "Windows"
    return False


def parse_json_string(string):
    if string is None:
        return None
    if string.startswith("{") and string.endswith("}"):
        return json.loads(string)
    return string


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


def unzip_descriptor(path, innerpath):
    frictionless = import_module("frictionless")
    resource = frictionless.Resource(path=path, compression="")
    with frictionless.system.create_loader(resource) as loader:
        byte_stream = loader.byte_stream
        if loader.remote:
            byte_stream = tempfile.TemporaryFile()
            shutil.copyfileobj(loader.byte_stream, byte_stream)
            byte_stream.seek(0)
        with zipfile.ZipFile(byte_stream, "r") as zip:
            tempdir = tempfile.mkdtemp()
            zip.extractall(tempdir)
            atexit.register(shutil.rmtree, tempdir)
            descriptor = os.path.join(tempdir, innerpath)
    return descriptor


def parse_resource_hash(hash):
    if not hash:
        return (settings.DEFAULT_HASHING, "")
    parts = hash.split(":", maxsplit=1)
    if len(parts) == 1:
        return (settings.DEFAULT_HASHING, parts[0])
    return parts


def md_to_html(md):
    try:
        html = marko.convert(md)
        html = html.replace("\n", "")
        return html
    except Exception:
        return ""


def html_to_text(html):
    class HTMLFilter(HTMLParser):
        text = ""

        def handle_data(self, data):
            self.text += data
            self.text += " "

    parser = HTMLFilter()
    parser.feed(html)
    return parser.text.strip()


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


# Collections


# NOTE: we might need to move ControlledList/Dict to Metadata to incapsulate its behaviour


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


# Backports


def slugify(text, **options):
    # There is a conflict between python-slugify and awesome-slugify
    # So we import from a proper module manually

    # Import
    from slugify.slugify import slugify

    # Slugify
    slug = slugify(text, **options)
    return slug


class cached_property:
    # It can be removed after dropping support for Python 3.6 and Python 3.7

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
        val = cache.get(self.attrname, settings.UNDEFINED)
        if val is settings.UNDEFINED:
            with self.lock:
                # check if another thread filled cache while we awaited lock
                val = cache.get(self.attrname, settings.UNDEFINED)
                if val is settings.UNDEFINED:
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


# Markdown


def render_markdown(path: str, data: dict) -> str:
    """Render any JSON-like object as Markdown, using jinja2 template"""

    template_dir = os.path.join(os.path.dirname(__file__), "assets/templates")
    environ = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir), lstrip_blocks=True, trim_blocks=True
    )
    environ.filters["filter_dict"] = filter_dict
    environ.filters["dict_to_markdown"] = json_to_markdown
    environ.filters["tabulate"] = dicts_to_markdown_table
    template = environ.get_template(path)
    return template.render(**data)


def filter_dict(
    x: dict, include: list = None, exclude: list = None, order: list = None
) -> dict:
    """Filter and order dictionary by key names"""

    if include:
        x = {key: x[key] for key in x if key in include}
    if exclude:
        x = {key: x[key] for key in x if key not in exclude}
    if order:
        index = [
            (order.index(key) if key in order else len(order), i)
            for i, key in enumerate(x)
        ]
        sorted_keys = [key for _, key in sorted(zip(index, x.keys()))]
        x = {key: x[key] for key in sorted_keys}
    return x


def json_to_markdown(
    x: Union[dict, list, int, float, str, bool],
    level: int = 0,
    tab: int = 2,
    flatten_scalar_lists: bool = True,
) -> str:
    """Render any JSON-like object as Markdown, using nested bulleted lists"""

    def _scalar_list(x) -> bool:
        return isinstance(x, list) and all(not isinstance(xi, (dict, list)) for xi in x)

    def _iter(x: Union[dict, list, int, float, str, bool], level: int = 0) -> str:
        if isinstance(x, (dict, list)):
            if isinstance(x, dict):
                labels = [f"- `{key}`" for key in x]
            elif isinstance(x, list):
                labels = [f"- [{i + 1}]" for i in range(len(x))]
            values = x if isinstance(x, list) else list(x.values())
            if isinstance(x, list) and flatten_scalar_lists:
                scalar = [not isinstance(value, (dict, list)) for value in values]
                if all(scalar):
                    values = [f"{values}"]
            lines = []
            for label, value in zip(labels, values):
                if isinstance(value, (dict, list)) and (
                    not flatten_scalar_lists or not _scalar_list(value)
                ):
                    lines.append(f"{label}\n{_iter(value, level=level + 1)}")
                else:
                    if isinstance(value, str):
                        # Indent to align following lines with '- '
                        value = jinja2.filters.do_indent(value, width=2, first=False)
                    lines.append(f"{label} {value}")
            txt = "\n".join(lines)
        else:
            txt = str(x)
        if level > 0:
            txt = jinja2.filters.do_indent(txt, width=tab, first=True, blank=False)
        return txt

    return jinja2.filters.do_indent(
        _iter(x, level=0), width=tab * level, first=True, blank=False
    )


def dicts_to_markdown_table(dicts: List[dict], **kwargs) -> str:
    """Tabulate dictionaries and render as a Markdown table"""

    if kwargs:
        dicts = [filter_dict(x, **kwargs) for x in dicts]
    try:
        pandas = import_module("pandas")
        df = pandas.DataFrame(dicts)
    except ImportError:
        module = import_module("frictionless.exception")
        errors = import_module("frictionless.errors")
        error = errors.GeneralError(note="Please install `pandas` package")
        raise module.FrictionlessException(error)
    return df.where(df.notnull(), None).to_markdown(index=False)
