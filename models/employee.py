class Employee:
    def __init__(self, id: int, name: str, initials: str, color: str):
        self.id = id
        self.name = name
        self.initials = initials
        self.color = color

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_dict(cls, data: dict) -> "Employee":
        return cls(
            id=data["id"],
            name=data["name"],
            initials=data["initials"],
            color=data["color"],
        )
