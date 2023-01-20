from __future__ import annotations
import subprocess as sp
from typing import TYPE_CHECKING
from ...resource import Resource
from ...system import Adapter
from .mapper import QsvMapper

if TYPE_CHECKING:
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
        with resource.open(as_file=True):
            while True:
                chunk = resource.read_bytes(size=BLOCK_SIZE)
                if not chunk:
                    break
                process.stdin.write(chunk)  # type: ignore
            process.stdin.close()  # type: ignore
            buffer = process.stdout.read()  # type: ignore
        stats = Resource(buffer, format="csv").extract()
        schema = QsvMapper().read_schema(stats)  # type: ignore
        return schema
