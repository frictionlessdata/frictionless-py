from __future__ import annotations
import os
from typing import TYPE_CHECKING, Union, Optional, List
from ...platform import platform
from ...system import Mapper

if TYPE_CHECKING:
    from ...metadata import Metadata


class MarkdownMapper(Mapper):
    """Markdown mapper"""

    def write_metadata(self, metadata: Metadata, *, table: bool = False):
        filename = metadata.__class__.__name__.lower()
        template = f"{filename}-table.md" if table is True else f"{filename}.md"
        descriptor = metadata.to_descriptor()
        text = render_markdown(f"{template}", {filename: descriptor}).strip()
        return text


# Internal


def render_markdown(path: str, data: dict) -> str:
    """Render any JSON-like object as Markdown, using jinja2 template"""

    # Create environ
    template_dir = os.path.join(os.path.dirname(__file__), "../../assets/templates")
    environ = platform.jinja2.Environment(
        loader=platform.jinja2.FileSystemLoader(template_dir),
        lstrip_blocks=True,
        trim_blocks=True,
    )

    # Render data
    environ.filters["filter_dict"] = filter_dict
    environ.filters["dict_to_markdown"] = dict_to_markdown
    environ.filters["tabulate"] = dicts_to_markdown_table
    template = environ.get_template(path)
    return template.render(**data)


def dict_to_markdown(
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
                        value = platform.jinja2_filters.do_indent(
                            value, width=2, first=False
                        )
                    lines.append(f"{label} {value}")
            txt = "\n".join(lines)
        else:
            txt = str(x)
        if level > 0:
            txt = platform.jinja2_filters.do_indent(
                txt, width=tab, first=True, blank=False
            )
        return txt

    return platform.jinja2_filters.do_indent(
        _iter(x, level=0), width=tab * level, first=True, blank=False
    )


def dicts_to_markdown_table(dicts: List[dict], **kwargs) -> str:
    """Tabulate dictionaries and render as a Markdown table"""
    if kwargs:
        dicts = [filter_dict(x, **kwargs) for x in dicts]
    df = platform.pandas.DataFrame(dicts)
    return df.where(df.notnull(), None).to_markdown(index=False)  # type: ignore


def filter_dict(
    x: dict,
    include: Optional[list] = None,
    exclude: Optional[list] = None,
    order: Optional[list] = None,
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
