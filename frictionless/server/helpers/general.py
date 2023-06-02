from tinydb.table import Table


class StringIndexedTable(Table):
    document_id_class = str

    def _get_next_id(self):
        raise RuntimeError("id must be provided")
