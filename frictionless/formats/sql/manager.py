from __future__ import annotations
import re
from typing import TYPE_CHECKING
from urllib.parse import urlsplit, urlunsplit
from .control import SqlControl
from ...package import Package
from ...package import Manager
from ...platform import platform
from ...resource import Resource
from .mapper import SqlMapper

if TYPE_CHECKING:
    from sqlalchemy import MetaData
    from sqlalchemy.engine import Engine
    from sqlalchemy.engine import Connection
    from ...schema import Schema


class SqlManager(Manager[SqlControl]):
    """Read and write data from/to SQL database"""

    def __init__(self, control: SqlControl, *, database_url: str):
        super().__init__(control)
        self.database_url = database_url
        source = database_url
        sa = platform.sqlalchemy

        # Create engine
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
        self.mapper = SqlMapper()

        # Add regex support
        # It will fail silently if this function already exists
        if self.connection.engine.dialect.name.startswith("sqlite"):
            self.connection.connection.create_function("REGEXP", 2, regexp)  # type: ignore

        # Create metadata and reflect
        self.metadata = sa.MetaData(bind=self.connection, schema=control.namespace)
        self.metadata.reflect(views=True)

    # State

    database_url: str
    """Database url"""

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
            resource = Resource(self.database_url, control=control)
            package.add_resource(resource)
        return package

    def read_schema(self):
        pass

    def read_row_stream(self):
        pass

    # Write

    def write_package(self, package: Package) -> None:
        for resource in package.resources:
            control = SqlControl(table=resource.name)
            resource.write(self.database_url, control=control)

    def write_schema(self, schema: Schema, *, table_name: str):
        table = self.mapper.from_schema(schema, engine=self.engine, table_name=table_name)
        self.metadata.create_all(tables=[table])

    def write_row_stream(self, row_stream, *, table_name: str):
        # TODO: review
        self.metadata.reflect()
        table = self.metadata.tables[table_name]
        buffer = []
        buffer_size = 1000
        for row in row_stream:
            cells = self.mapper.from_row(row)
            buffer.append(cells)
            if len(buffer) > buffer_size:
                # sqlalchemy conn.execute(table.insert(), buffer)
                # syntax applies executemany DB API invocation.
                self.connection.execute(table.insert().values(buffer))
                buffer = []
        if len(buffer):
            self.connection.execute(table.insert().values(buffer))


# Internal


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
