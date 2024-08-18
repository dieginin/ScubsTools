from tinydb import Query, TinyDB
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

    @staticmethod
    def check_existence(table: Table, **kwargs) -> str | None:
        """Check the existence of a value in a table."""
        for key, value in kwargs.items():
            if table.search(Query()[key] == value):
                return (
                    f"{table.name[:-1].capitalize()} with {key} {value} already exists."
                )
