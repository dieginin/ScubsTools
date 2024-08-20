import datetime as dt
from typing import Dict

from .employee import Employee


class SalesReport:
    def __init__(
        self,
        id: int,
        date: str,
        dollar_counts: Dict[int, int],
        cent_counts: Dict[int, int],
        littmanns: int,
        gift_cards: Dict[int, int],
        arrivals_times: Dict[Employee, str],
        departures_times: Dict[Employee, str],
        sales: Dict[str, list] = {"cash": [0, 0], "card": [0, 0], "gift": [0, 0]},
    ):
        self.id = id
        self.date = date
        self.dollar_counts = dollar_counts
        self.cent_counts = cent_counts
        self.littmanns = littmanns
        self.gift_cards = gift_cards
        self.arrivals_times = arrivals_times
        self.departures_times = departures_times
        self.__sales = sales

    @property
    def cash_sales(self) -> tuple[int, float]:
        return tuple(self.__sales["cash"])

    @property
    def card_sales(self) -> tuple[int, float]:
        return tuple(self.__sales["card"])

    @property
    def gift_sales(self) -> tuple[int, float]:
        return tuple(self.__sales["gift"])

    @property
    def is_closed(self) -> bool:
        cash_sales = self.cash_sales[0] != 0 or self.cash_sales[1] != 0
        card_sales = self.card_sales[0] != 0 or self.card_sales[1] != 0
        gift_sales = self.gift_sales[0] != 0 or self.gift_sales[1] != 0
        return cash_sales or card_sales or gift_sales

    def __repr__(self) -> str:
        return self.date

    def __str__(self) -> str:
        return self.date
