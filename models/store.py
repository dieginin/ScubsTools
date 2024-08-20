class Store:
    def __init__(self, id: int, name: str, initials: str):
        self.id = id
        self.name = name
        self.initials = initials

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return self.name

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "initials": self.initials}

    @classmethod
    def from_dict(cls, data: dict) -> "Store":
        return cls(id=data["id"], name=data["name"], initials=data["initials"])
