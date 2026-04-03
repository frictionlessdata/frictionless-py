from __future__ import annotations

from ...platform import platform
from ...resources import TableResource
from ...system import Parser
from .control import ParquetControl


class ParquetParser(Parser):
    """Parquet parser implementation."""

    supported_types = [
        "array",
        "boolean",
        "datetime",
        "date",
        "duration",
        "integer",
        "number",
        "object",
        "string",
        "time",
    ]

    # Read

    def read_cell_stream_create(self):
        control = ParquetControl.from_dialect(self.resource.dialect)
        handle = self.resource.normpath
        if self.resource.remote:
            handles = platform.pandas.io.common.get_handle(  # type: ignore
                self.resource.normpath, "rb", is_text=False
            )
            handle = handles.handle
        pq = platform.pyarrow_parquet
        table = pq.read_table(
            handle,
            columns=control.columns,
            filters=control.filters or None,
        )
        df = table.to_pandas(categories=control.categories or None)
        with TableResource(data=df, format="pandas") as resource:
            yield from resource.cell_stream

    # Write

    def write_row_stream(self, source: TableResource):
        import pyarrow as pa

        pq = platform.pyarrow_parquet
        df = source.to_pandas()
        table = pa.Table.from_pandas(df)
        pq.write_table(table, self.resource.normpath)
