from tinydb import Query

from models import Store

from .database import Database


class Stores:
    def __init__(self):
        self.__table = Database().db.table("stores")

    def add(self, name: str, initials: str) -> str:
        id = Database.get_next_id(self.__table)

        # Check if an store already exists
        if existing_employee := Database.check_existence(
            self.__table, name=name, initials=initials
        ):
            return existing_employee

        # Add new store if no duplicates found
        self.__table.insert({"id": id, "name": name, "initials": initials})
        return f"Store {name} added with ID {id}."

    def remove(self, store: Store) -> str:
        if self.__table.remove(Query().id == store.id):
            return f"Store {store.name} removed."
        else:
            return f"Store not found."

    @property
    def list(self) -> list[Store]:
        return sorted(
            [
                Store(sto["id"], sto["name"], sto["initials"])
                for sto in self.__table.all()
            ],
            key=lambda sto: sto.name,
        )
