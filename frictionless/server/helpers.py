import re
import stringcase  # type: ignore
from tinydb.table import Table
from slugify.slugify import slugify


def make_id(name: str):
    id = slugify(name)
    id = re.sub(f"[^a-zA-Z0-9]+", "_", name)
    id = stringcase.camelcase(id)  # type: ignore
    return id


class StringIndexedTable(Table):
    document_id_class = str

    def _get_next_id(self):
        raise RuntimeError("id must be provided")
