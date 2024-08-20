from tinydb import Query

from models import Store

from .database import Database


class Stores:
    def __init__(self):
        self.__table = Database().db.table("stores")

    @property
    def list(self) -> list[Store]:
        return sorted(
            [Store.from_dict(sto) for sto in self.__table.all()],
            key=lambda sto: sto.name,
        )

    def get(self, id: int) -> Store | None:
        store = self.__table.get(Query().id == id)
        if not store:
            return None
        return Store.from_dict(store)  # type: ignore

    def add(self, name: str, initials: str) -> str:
        id = Database.get_next_id(self.__table)

        # Check if an store already exists
        if existing_store := Database.check_existence(
            self.__table, name=name, initials=initials
        ):
            return existing_store

        # Add new store if no duplicates found
        self.__table.insert({"id": id, "name": name, "initials": initials})
        return f"Store {name} added with ID {id}."

    def edit(
        self, store: Store, name: str | None = None, initials: str | None = None
    ) -> str:
        if existing_store := Database.check_existence(
            self.__table, name=name, initials=initials
        ):
            return existing_store

        self.__table.update(
            {"name": name or store.name, "initials": initials or store.initials},
            Query().id == store.id,
        )
        return f"Store {name or store.name} updated."

    def remove(self, store: Store) -> str:
        if self.__table.remove(Query().id == store.id):
            return f"Store {store.name} removed."
        else:
            return f"Store not found."
