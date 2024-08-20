from tinydb import Query

from models import Employee

from .database import Database


class Employees:
    def __init__(self):
        self.__table = Database().db.table("employees")

    @property
    def list(self) -> list[Employee]:
        return sorted(
            [Employee.from_dict(emp) for emp in self.__table.all()],
            key=lambda emp: emp.name,
        )

    def add(self, name: str, initials: str, color: str) -> str:
        id = Database.get_next_id(self.__table)

        # Check if an employee already exists
        if existing_employee := Database.check_existence(
            self.__table, name=name, initials=initials, color=color
        ):
            return existing_employee

        # Add new employee if no duplicates found
        self.__table.insert(
            {"id": id, "name": name, "initials": initials, "color": color}
        )
        return f"Employee {name} added with ID {id}."

    def edit(
        self,
        employee: Employee,
        name: str | None = None,
        initials: str | None = None,
        color: str | None = None,
    ) -> str:
        if existing_store := Database.check_existence(
            self.__table, name=name, initials=initials, color=color
        ):
            return existing_store

        self.__table.update(
            {
                "name": name or employee.name,
                "initials": initials or employee.initials,
                "color": color or employee.color,
            },
            Query().id == employee.id,
        )
        return f"Employee {name or employee.name} updated."

    def remove(self, employee: Employee) -> str:
        if self.__table.remove(Query().id == employee.id):
            return f"Employee {employee.name} removed."
        else:
            return f"Employee not found."
