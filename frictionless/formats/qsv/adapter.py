from __future__ import annotations

import subprocess as sp
from typing import TYPE_CHECKING

from ...resources import TableResource
from ...system import Adapter
from .mapper import QsvMapper

if TYPE_CHECKING:
    from ...resource import Resource
    from ...schema import Schema


BLOCK_SIZE = 8096


class QsvAdapter(Adapter):
    qsv_path: str

    def __init__(self, qsv_path: str):
        self.qsv_path = qsv_path

    # Read

    def read_schema(self, resource: Resource) -> Schema:
        command = [self.qsv_path, "stats", "--infer-dates", "--dates-whitelist", "all"]
        process = sp.Popen(command, stdout=sp.PIPE, stdin=sp.PIPE)
        # TODO: Use FileResource here (or future resource.stream_bytes())
        with resource:
            while True:
                chunk = resource.read_bytes(size=BLOCK_SIZE)
                if not chunk:
                    break
                process.stdin.write(chunk)  # type: ignore
            process.stdin.close()  # type: ignore
            buffer = process.stdout.read()  # type: ignore
        result = TableResource(data=buffer, format="csv")
        stats = result.read_rows()
        schema = QsvMapper().read_schema(stats)  # type: ignore
        return schema
