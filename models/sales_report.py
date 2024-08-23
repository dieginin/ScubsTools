from datetime import date as dt
from datetime import datetime, time
from typing import Dict, List, Optional

from .employee import Employee
from .store import Store


class MoneyCount:
    def __init__(self, bills: Dict[str, int], cents: Dict[str, int]):
        self.bills = bills
        self.cents = cents

    def to_dict(self) -> dict:
        return {"bills": self.bills, "cents": self.cents}

    @classmethod
    def from_dict(cls, data: dict) -> "MoneyCount":
        return cls(bills=data["bills"], cents=data["cents"])


class GiftCards:
    def __init__(self, fifty: int, t_five: int):
        self.fifty = fifty
        self.t_five = t_five

    def to_dict(self) -> dict:
        return {"fifty": self.fifty, "t_five": self.t_five}

    @classmethod
    def from_dict(cls, data: dict) -> "GiftCards":
        return cls(fifty=data["fifty"], t_five=data["t_five"])


class Counts:
    def __init__(self, littmanns: int, gift_cards: GiftCards):
        self.littmanns = littmanns
        self.gift_cards = gift_cards

    def to_dict(self) -> dict:
        return {"littmanns": self.littmanns, "gift_cards": self.gift_cards.to_dict()}

    @classmethod
    def from_dict(cls, data: dict) -> "Counts":
        return cls(
            littmanns=data["littmanns"],
            gift_cards=GiftCards.from_dict(data["gift_cards"]),
        )


class EmployeeTime:
    def __init__(self, employee: Employee, time: time):
        self.employee = employee
        self.time = time

    def to_dict(self) -> dict:
        return {"employee": self.employee.id, "time": self.time.strftime("%H:%M")}

    @classmethod
    def from_dict(cls, data: dict) -> "EmployeeTime":
        from databases import Employees

        return cls(
            employee=Employees().get(data["employee"]) or Employee(0, "", "", ""),
            time=datetime.strptime(data["time"], "%H:%M").time(),
        )


class Schedule:
    def __init__(self, arrivals: List[EmployeeTime], departures: List[EmployeeTime]):
        self.arrivals = arrivals
        self.departures = departures

    @property
    def working_hours(self) -> tuple[time, time]:
        open_hr = time(23, 0)
        for arrival in self.arrivals:
            if arrival.time < open_hr:
                open_hr = arrival.time

        close_hr = time(0, 0)
        for departure in self.departures:
            if departure.time > close_hr:
                close_hr = departure.time
        return open_hr, close_hr

    def to_dict(self) -> dict:
        return {
            "arrivals": [x.to_dict() for x in self.arrivals],
            "departures": [x.to_dict() for x in self.departures],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Schedule":
        arrivals = [EmployeeTime.from_dict(d) for d in data["arrivals"]]
        departures = [EmployeeTime.from_dict(d) for d in data["departures"]]
        return cls(arrivals=arrivals, departures=departures)


class MType:
    def __init__(self, qty: int, amount: float):
        self.qty = qty
        self.amount = amount

    def to_dict(self) -> dict:
        return {"qty": self.qty, "amount": self.amount}

    @classmethod
    def from_dict(cls, data: dict) -> "MType":
        return cls(qty=data["qty"], amount=data["amount"])


class Movements:
    def __init__(self, cash: MType, card: MType, gift: MType):
        self.cash = cash
        self.card = card
        self.gift = gift

    @property
    def count(self) -> int:
        return self.cash.qty + self.card.qty + self.gift.qty

    @property
    def amount(self) -> float:
        return self.cash.amount + self.card.amount + self.gift.amount

    def to_dict(self) -> dict:
        return {
            "cash": self.cash.to_dict(),
            "card": self.card.to_dict(),
            "gift": self.gift.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Movements":
        return cls(
            cash=MType.from_dict(data["cash"]),
            card=MType.from_dict(data["card"]),
            gift=MType.from_dict(data["gift"]),
        )


class SalesReport:
    def __init__(
        self,
        id: int,
        date: dt,
        store: Store,
        schedule: Schedule,
        money_open: MoneyCount,
        counts_open: Counts,
        money_close: Optional[MoneyCount] = None,
        counts_close: Optional[Counts] = None,
        returns: Optional[Movements] = None,
        sales: Optional[Movements] = None,
    ) -> None:
        self.id = id
        self.date = date
        self.store = store
        self.schedule = schedule
        self.money_open = money_open
        self.money_close = money_close
        self.counts_open = counts_open
        self.counts_close = counts_close
        self.returns = returns
        self.sales = sales

    def __repr__(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    def __str__(self) -> str:
        return self.date.strftime("%Y-%m-%d")

    @classmethod
    def from_dict(cls, data: dict) -> "SalesReport":
        from databases import Stores

        return cls(
            id=data["id"],
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            store=Stores().get(data["store"]) or Store(0, "", ""),
            schedule=Schedule.from_dict(data["schedule"]),
            money_open=MoneyCount.from_dict(data["money_open"]),
            counts_open=Counts.from_dict(data["counts_open"]),
            money_close=(
                MoneyCount.from_dict(data["money_close"])
                if data.get("money_close")
                else None
            ),
            counts_close=(
                Counts.from_dict(data["counts_close"])
                if data.get("counts_close")
                else None
            ),
            returns=(
                Movements.from_dict(data["returns"]) if data.get("returns") else None
            ),
            sales=Movements.from_dict(data["sales"]) if data.get("sales") else None,
        )
