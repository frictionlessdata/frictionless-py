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
    from sqlalchemy.engine import Connection


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
        engine = sa.create_engine(source) if isinstance(source, str) else source

        # Set attributes
        control = control or SqlControl()
        self.connection = engine.connect()
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

    metadata: MetaData
    """SqlAlchemy's metadata"""

    connection: Connection
    """SqlAlchemy's connection"""

    mapper: SqlMapper
    """Mapper instance"""

    # Read

    def read_package(self) -> Package:
        package = Package(resources=[])
        for sql_table in self.metadata.sorted_tables:
            control = SqlControl(table=sql_table.name)
            resource = Resource(self.database_url, control=control)
            package.add_resource(resource)
        return package

    # Write

    def write_package(self, package: Package) -> None:
        pass


# Internal


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None
