from tinydb import Query

from helpers import get_today_date
from models import SalesReport, Store
from models.sales_report import Counts, MoneyCount, Movements, Schedule

from .database import Database


class SalesReports:
    def __init__(self):
        self.__table = Database().db.table("sales_reports")

    @property
    def list(self) -> list[SalesReport]:
        return sorted(
            [SalesReport.from_dict(sr) for sr in self.__table.all()],
            key=lambda sr: sr.date,
        )

    def __check_open(self, date: str) -> bool:
        return bool(Database.check_existence(self.__table, date=date))

    def __check_close(self, date: str) -> bool:
        if Database.check_existence(self.__table, date=date):
            return bool(
                self.__table.search(Query().date == date and Query().sales != None)
            )
        return False

    def open(
        self, store: Store, schedule: Schedule, money_count: MoneyCount, counts: Counts
    ) -> str:
        today_date = get_today_date()

        if self.__check_close(today_date):
            return "The store already closed today."

        if self.__check_open(today_date):
            return "The store already opened today."

        id = Database.get_next_id(self.__table)
        self.__table.insert(
            {
                "id": id,
                "date": today_date,
                "store": store.id,
                "schedule": schedule.to_dict(),
                "money_open": money_count.to_dict(),
                "counts_open": counts.to_dict(),
            }
        )
        return f"Store's sales report {id} for {today_date} started."

    def close(
        self,
        sales_report: SalesReport,
        money_count: MoneyCount,
        counts: Counts,
        returns: Movements,
        sales: Movements,
    ) -> str:
        if not self.__check_open(sales_report.date.strftime("%Y-%m-%d")):
            return "The store hasn't open yet."

        if self.__check_close(sales_report.date.strftime("%Y-%m-%d")):
            return "The store already closed."

        self.__table.update(
            {
                "money_close": money_count.to_dict(),
                "counts_close": counts.to_dict(),
                "returns": returns.to_dict(),
                "sales": sales.to_dict(),
            },
            Query().id == sales_report.id,
        )
        return f"Store's sales report {sales_report.id} closed."
