from __future__ import annotations
import re
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit
from .control import SqlControl
from ...package import Package, Adapter
from ...platform import platform
from ...resource import Resource
from .mapper import SqlMapper

if TYPE_CHECKING:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine
    from sqlalchemy.engine import Connection
    from ...schema import Schema


class SqlAdapter(Adapter[SqlControl]):
    """Read and write data from/to SQL database"""

    def __init__(self, control: SqlControl):
        super().__init__(control)
        sa = platform.sqlalchemy

        # TODO: rework
        # Create engine
        assert control.driver
        source = sa.engine.URL(
            drivername=control.driver,
            username=control.user,
            password=control.password,
            host=control.host,
            port=control.port,
            database=control.database,
            query={},  # type: ignore
        ).render_as_string()
        if control and control.basepath:
            url = urlsplit(source)
            basepath = control.basepath
            if isinstance(source, str) and source.startswith("sqlite"):
                # Path for sqlite looks like this 'sqlite:///path' (unix/windows)
                basepath = f"/{basepath}"
            source = urlunsplit((url.scheme, basepath, url.path, url.query, url.fragment))
        self.engine = sa.create_engine(source) if isinstance(source, str) else source

        # Set attributes
        control = control or SqlControl()
        self.connection = self.engine.connect()
        self.mapper = SqlMapper(self.engine)

        # Add regex support
        # It will fail silently if this function already exists
        if self.connection.engine.dialect.name.startswith("sqlite"):
            self.connection.connection.create_function("REGEXP", 2, regexp)  # type: ignore

        # Create metadata and reflect
        self.metadata = sa.MetaData(bind=self.connection, schema=control.namespace)
        self.metadata.reflect(views=True)

    # State

    engine: Engine
    """SqlAlchemy's engine"""

    metadata: MetaData
    """SqlAlchemy's metadata"""

    connection: Connection
    """SqlAlchemy's connection"""

    mapper: SqlMapper
    """Mapper instance"""

    # Read

    def read_package(self) -> Package:
        package = Package(resources=[])
        for table in self.metadata.sorted_tables:
            control = SqlControl(table=table.name)
            resource = Resource(self.engine.url.render_as_string(), control=control)
            package.add_resource(resource)
        return package

    def read_schema(self, table_name: str):
        table = self.metadata.tables[table_name]
        return self.mapper.read_schema(table)

    def read_cell_stream(self, control):
        sa = platform.sqlalchemy
        self.metadata.reflect()
        table = self.metadata.tables[control.table]
        with self.connection.begin():
            # Streaming could be not working for some backends:
            # http://docs.sqlalchemy.org/en/latest/core/connections.html
            select = table.select().execution_options(stream_results=True)
            if control.order_by:
                select = select.order_by(sa.sql.text(control.order_by))
            if control.where:
                select = select.where(sa.sql.text(control.where))
            result = select.execute()
            yield list(result.keys())
            for item in result:
                cells = list(item)
                yield cells

    # Write

    def write_package(self, package: Package) -> None:
        for resource in package.resources:
            control = SqlControl(table=resource.name)
            resource.write(self.engine.url.render_as_string(), control=control)

    def write_schema(self, schema: Schema, *, table_name: str):
        table = self.mapper.write_schema(schema, table_name=table_name)
        self.metadata.create_all(tables=[table])

    def write_row_stream(self, row_stream, *, table_name: str):
        # TODO: review
        self.metadata.reflect()
        table = self.metadata.tables[table_name]
        buffer = []
        buffer_size = 1000
        for row in row_stream:
            cells = self.mapper.write_row(row)
            buffer.append(cells)
            if len(buffer) > buffer_size:
                # sqlalchemy conn.execute(table.insert(), buffer)
                # syntax applies executemany DB API invocation.
                self.connection.execute(table.insert().values(buffer))
                buffer = []
        if len(buffer):
            self.connection.execute(table.insert().values(buffer))

    # Convert

    @classmethod
    def from_source(cls, source: str, *, control=None):
        engine = platform.sqlalchemy.create_engine(source)
        control = SqlControl()
        control.driver = engine.url.drivername
        control.user = engine.url.username
        control.password = engine.url.password  # type: ignore
        control.host = engine.url.host
        control.port = engine.url.port
        control.database = engine.url.database
        # TODO: improve
        return cls(control)  # type: ignore


# Internal


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
