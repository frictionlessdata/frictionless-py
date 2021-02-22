---
title: Format Guide
---

In Frictionless Framework a format is a set of concepts associated with a data source protocol:
- Dialect
- Parser

The Parser is responsible for parsing data from/to different data sources as though CSV or Excel. The Dialect is a simple object to configure the Parser.

## Parser Example

> This parser has quite a naive experimental implementation

```python title="Python"
class HtmlParser(Parser):
    requires_loader = True
    supported_types = [
        "string",
    ]

    # Read

    def read_list_stream_create(self):
        pq = helpers.import_from_plugin("pyquery", plugin="html").PyQuery
        dialect = self.resource.dialect

        # Get Page content
        page = pq(self.loader.text_stream.read(), parser="html")

        # Find required table
        if dialect.selector:
            table = pq(page.find(dialect.selector)[0])
        else:
            table = page

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
        with tempfile.NamedTemporaryFile("wt", delete=False) as file:
            file.write(html)
        loader = system.create_loader(target)
        result = loader.write_byte_stream(file.name)
        return result
```

## Dialect Example


```python title="Python"
class HtmlDialect(Dialect):

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
```

## References

- [Parser](../../references/api-reference.md#parser)
- [Dialect](../../references/api-reference.md#dialect)
