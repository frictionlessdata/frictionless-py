from __future__ import annotations
import builtins
from typing import TYPE_CHECKING, Optional, Dict, Union, Any, List
from ...platform import platform
from ...resource import Resource
from ...system import system
from .analyze import analyze
from .transform import transform
from .validate import validate
from ... import settings

if TYPE_CHECKING:
    from ...formats.sql import IOnRow, IOnProgress
    from ...interfaces import IFilterFunction, IProcessFunction, ITabularData
    from ...interfaces import ICallbackFunction
    from ...checklist import Checklist
    from ...pipeline import Pipeline
    from ...dialect import Control


class TableResource(Resource):
    type = "table"
    datatype = "table"
    tabular = True

    # Analyze

    def analyze(self, *, detailed=False) -> Dict:
        """Analyze the resource

        This feature is currently experimental, and its API may change
        without warning.

        Parameters:
            detailed? (bool): detailed analysis

        Returns:
            dict: resource analysis

        """
        return analyze(self, detailed=detailed)

    # Extract

    def extract(
        self,
        *,
        name: Optional[str] = None,
        filter: Optional[IFilterFunction] = None,
        process: Optional[IProcessFunction] = None,
        limit_rows: Optional[int] = None,
    ) -> ITabularData:
        if not process:
            process = lambda row: row.to_dict()
        data = self.read_rows(size=limit_rows)
        data = builtins.filter(filter, data) if filter else data
        data = (process(row) for row in data) if process else data
        return {name or self.name: list(data)}

    # Index

    def index(
        self,
        database_url: str,
        *,
        name: Optional[str] = None,
        fast: bool = False,
        on_row: Optional[IOnRow] = None,
        on_progress: Optional[IOnProgress] = None,
        use_fallback: bool = False,
        qsv_path: Optional[str] = None,
    ) -> List[str]:
        name = name or self.name
        indexer = platform.frictionless_formats.sql.SqlIndexer(
            resource=self,
            database_url=database_url,
            table_name=name,
            fast=fast,
            on_row=on_row,
            on_progress=on_progress,
            use_fallback=use_fallback,
            qsv_path=qsv_path,
        )
        indexer.index()
        return [name]

    # Transform

    def transform(self, pipeline: Pipeline):
        return transform(self, pipeline)

    # Validate

    def validate(
        self,
        checklist: Optional[Checklist] = None,
        *,
        name: Optional[str] = None,
        on_row: Optional[ICallbackFunction] = None,
        parallel: bool = False,
        limit_rows: Optional[int] = None,
        limit_errors: int = settings.DEFAULT_LIMIT_ERRORS,
    ):
        return validate(
            self,
            checklist,
            on_row=on_row,
            limit_rows=limit_rows,
            limit_errors=limit_errors,
        )

    # Write

    def write(
        self,
        target: Optional[Union[Resource, Any]] = None,
        *,
        control: Optional[Control] = None,
        **options,
    ) -> Resource:
        """Write this resource to the target resource

        Parameters:
            target (Resource|Any): target or target resource instance
            **options (dict): Resource constructor options
        """
        resource = target
        if not isinstance(resource, Resource):
            resource = Resource(target, control=control, **options)
        parser = system.create_parser(resource)
        parser.write_row_stream(self)
        return resource
