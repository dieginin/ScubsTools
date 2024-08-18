from tinydb import Query

from models import Employee

from .database import Database


class Employees:
    def __init__(self):
        self.__table = Database().db.table("employees")

    def add(self, name: str, initials: str, color: str) -> str:
        id = Database.get_next_id(self.__table)

        # Check if an employee with the same name, initials, and color already exists
        existing_employee = self.__table.search(
            (Query().name == name)
            & (Query().initials == initials)
            & (Query().color == color)
        )
        if existing_employee:
            return f"Employee with Name '{name}', Initials '{initials}', and Color '{color}' already exists."

        # Check for individual duplicates
        existing_name = self.__table.search(Query().name == name)
        if existing_name:
            return f"Employee with Name '{name}' already exists."
        existing_initials = self.__table.search(Query().initials == initials)
        if existing_initials:
            return f"Employee with Initials '{initials}' already exists."
        existing_color = self.__table.search(Query().color == color)
        if existing_color:
            return f"Employee with Color '{color}' already exists."

        # Add new employee if no duplicates found
        self.__table.insert(
            {"id": id, "name": name, "initials": initials, "color": color}
        )
        return f"Employee {name} added with ID {id}."

    def remove(self, employee: Employee) -> str:
        if self.__table.remove(Query().id == employee.id):
            return f"Employee {employee.name} removed."
        else:
            return f"Employee not found."

    @property
    def list(self) -> list[Employee]:
        return sorted(
            [
                Employee(emp["id"], emp["name"], emp["initials"], emp["color"])
                for emp in self.__table.all()
            ],
            key=lambda emp: emp.name,
        )
