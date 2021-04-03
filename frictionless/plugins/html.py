import tempfile
from ..metadata import Metadata
from ..dialect import Dialect
from ..plugin import Plugin
from ..parser import Parser
from ..system import system
from .. import helpers


# Plugin


class HtmlPlugin(Plugin):
    """Plugin for HTML

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.html import HtmlPlugin`

    """

    code = "html"
    status = "experimental"

    def create_dialect(self, resource, *, descriptor):
        if resource.format == "html":
            return HtmlDialect(descriptor)

    def create_parser(self, resource):
        if resource.format == "html":
            return HtmlParser(resource)


# Dialect


class HtmlDialect(Dialect):
    """Html dialect representation

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.html import HtmlDialect`

    Parameters:
        descriptor? (str|dict): descriptor
        selector? (str): HTML selector

    Raises:
        FrictionlessException: raise any error that occurs during the process

    """

    def __init__(self, descriptor=None, *, selector=None):
        self.setinitial("selector", selector)
        super().__init__(descriptor)

    @Metadata.property
    def selector(self):
        """
        Returns:
            str: selector
        """
        return self.get("selector", "table")

    # Expand

    def expand(self):
        """Expand metadata"""
        self.setdefault("selector", self.selector)

    # Metadata

    metadata_profile = {  # type: ignore
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "selector": {"type": "string"},
        },
    }


# Parser


class HtmlParser(Parser):
    """HTML parser implementation.

    API      | Usage
    -------- | --------
    Public   | `from frictionless.plugins.html import HtmlParser`

    """

    requires_loader = True
    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        pq = helpers.import_from_plugin("pyquery", plugin="html").PyQuery

        # Get table
        page = pq(self.loader.text_stream.read(), parser="html")
        tables = page.find(self.resource.dialect.selector)
        table = pq(tables[0]) if tables else None
        if not table:
            return

        # Stream headers
        data = (
            table.children("thead").children("tr")
            + table.children("thead")
            + table.children("tr")
            + table.children("tbody").children("tr")
        )
        data = [pq(r) for r in data if len(r) > 0]
        first_row = data.pop(0)
        headers = [pq(th).text() for th in first_row.find("th,td")]
        yield headers

        # Stream data
        data = [pq(tr).find("td") for tr in data]
        data = [[pq(td).text() for td in tr] for tr in data if len(tr) > 0]
        yield from data

    # Write

    # NOTE:
    # We can rebase on pyquery for writing this html
    # It will give us an ability to support HtmlDialect
    def write_row_stream(self, resource):
        source = resource
        target = self.resource
        html = "<html><body><table>\n"
        with source:
            for row in source.row_stream:
                if row.row_number == 1:
                    html += "<tr>"
                    for name in row.field_names:
                        html += f"<td>{name}</td>"
                    html += "</tr>\n"
                cells = row.to_list(types=self.supported_types)
                html += "<tr>"
                for cell in cells:
                    html += f"<td>{cell}</td>"
                html += "</tr>\n"
        html += "</table></body></html>"
        with tempfile.NamedTemporaryFile(
            "wt", delete=False, encoding=target.encoding
        ) as file:
            file.write(html)
        loader = system.create_loader(target)
        result = loader.write_byte_stream(file.name)
        return result
