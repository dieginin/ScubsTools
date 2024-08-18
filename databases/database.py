from tinydb import TinyDB
from tinydb.table import Table


class Database:
    def __init__(self):
        self.db = TinyDB("database.json")

    @staticmethod
    def get_next_id(table: Table) -> int:
        """Retrieve the next available ID."""
        if not table.all():
            return 1
        max_id = max(employee["id"] for employee in table.all())
        return max_id + 1
