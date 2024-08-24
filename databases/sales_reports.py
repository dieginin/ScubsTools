from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    Paragraph,
    ParagraphAndImage,
    SimpleDocTemplate,
    Table,
    TableStyle,
)
from tinydb import Query

from helpers import count_money, get_today_date
from models import SalesReport, Store
from models.sales_report import Counts, MoneyCount, Movements, Schedule

from .database import Database


class SalesReports:
    def __init__(self):
        self.__table = Database().db.table("sales_reports")

    @property
    def sales_report_list(self) -> list[SalesReport]:
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

    def generate_report(self, sales_report: SalesReport):
        def __create_table(
            data: list[list],
            style: list[tuple],
            colWidths: list | None = None,
            rowHeights: list | None = None,
            spaceBefore: float | None = None,
        ) -> Table:
            create_style = lambda s: TableStyle(s)

            return Table(
                data,
                colWidths,
                rowHeights,
                create_style(style),
                spaceBefore=spaceBefore,
            )

        def __create_counts_table(
            money: MoneyCount | None, counts: Counts | None
        ) -> Table:
            bills = money.bills if money else {}
            cents = money.cents if money else {}
            gift_cards = counts.gift_cards if counts else None

            return __create_table(
                data=[
                    ["$100", bills.get("100", 0), "¢25", cents.get("25", 0)],
                    ["$50", bills.get("50", 0), "¢10", cents.get("10", 0)],
                    ["$20", bills.get("20", 0), "¢5", cents.get("5", 0)],
                    ["$10", bills.get("10", 0), "¢1", cents.get("1", 0)],
                    ["$5", bills.get("5", 0), "Gift cards", ""],
                    [
                        "$2",
                        bills.get("2", 0),
                        50,
                        gift_cards.fifty if gift_cards else 0,
                    ],
                    [
                        "$1",
                        bills.get("1", 0),
                        25,
                        gift_cards.t_five if gift_cards else 0,
                    ],
                    ["Littmanns", "", counts.littmanns if counts else 0, ""],
                    ["Total", "", f"${count_money(bills, cents)}", ""],
                ],
                style=[
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("ALIGN", (0, -2), (1, -1), "RIGHT"),
                    ("BOX", (2, -5), (-1, -3), 0.5, colors.grey),
                    ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ("FONTNAME", (-2, 0), (-2, -3), "Helvetica-Bold"),
                    ("LINEABOVE", (2, -4), (-1, -4), 0.5, colors.grey),
                    ("SPAN", (2, 4), (-1, 4)),
                    ("SPAN", (2, -1), (-1, -1)),
                    ("SPAN", (0, -2), (1, -2)),
                    ("SPAN", (0, -1), (1, -1)),
                    ("SPAN", (-2, -2), (-1, -2)),
                    ("TEXTCOLOR", (1, 0), (1, -3), colors.grey),
                    ("TEXTCOLOR", (3, 0), (3, -3), colors.grey),
                    ("TEXTCOLOR", (2, -2), (2, -1), colors.grey),
                ],
            )

        def __create_movements_table(title: str, movements: Movements | None) -> Table:
            if movements:
                amounts = [
                    movements.card.amount,
                    movements.cash.amount,
                    movements.gift.amount,
                ]
                counts = [movements.card.qty, movements.cash.qty, movements.gift.qty]
                count = movements.count
                amount = movements.amount
            else:
                amounts = [0, 0, 0]
                counts = [0, 0, 0]
                count = 0
                amount = 0
            return __create_table(
                data=[
                    [title, "", ""],
                    ["Cash", "Card", "Gift card"],
                    counts,
                    [f"${amounts[0]}", f"${amounts[1]}", f"${amounts[2]}"],
                    [f"{count}  ◊  ${amount}", "", ""],
                ],
                style=[
                    ("SPAN", (0, 0), (-1, 0)),
                    ("SPAN", (0, -1), (-1, -1)),
                    ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
                    # ("FONTNAME", (0, -1), (0, -1), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 23),
                    ("FONTSIZE", (0, 1), (-1, 1), 15),
                    ("FONTSIZE", (0, -1), (-1, -1), 13),
                    ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("TEXTCOLOR", (0, 2), (-1, 2), colors.grey),
                    ("TEXTCOLOR", (0, -1), (-1, -1), colors.grey),
                ],
                colWidths=[1.5 * inch],
                rowHeights=[
                    0.65 * inch,
                    0.45 * inch,
                    0.28 * inch,
                    0.28 * inch,
                    0.35 * inch,
                ],
            )

        elements = []
        file_name = f"sales_report_{sales_report.date}.pdf"
        pdf = SimpleDocTemplate(file_name, pagesize=letter)

        # Set attributes
        pdf.title = "Daily Sales Report"
        pdf.author = "Diego Balestra"
        pdf.creator = "Scrubs Boutique and More"

        pdf.topMargin = 5
        pdf.bottomMargin = 5
        pdf.leftMargin = 20
        pdf.rightMargin = 20

        ## HEADER ##
        image = Image("assets/scrubs_logo.png", 330 / 2.5, 149 / 2.5)

        title_text = """<font name=Helvetica-Bold color=black size=19>Daily Sales Report</font> <font name=Helvetica color=grey size=8>v8</font><br/>
        <font name=Helvetica color=grey size=12>Scrubs Boutique and More LLC</font>"""
        header = ParagraphAndImage(Paragraph(title_text), image, ypad=20)
        elements.append(header)

        ## DATA ##
        store_name = sales_report.store.name
        store_open, store_close = sales_report.schedule.working_hours
        working_hours = store_close.hour - store_open.hour
        date = sales_report.date.strftime("%B %d, %Y")

        data = __create_table(
            data=[["Store", "Hours", "Date"], [store_name, working_hours, date]],
            style=[
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 18),
                ("FONTSIZE", (0, 1), (-1, 1), 14),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
            colWidths=[2.5 * inch],
            rowHeights=[0.45 * inch, 0.3 * inch],
            spaceBefore=65,
        )
        elements.append(data)

        ## COUNTS ##
        open_counts = __create_counts_table(
            sales_report.money_open, sales_report.counts_open
        )
        close_counts = __create_counts_table(
            sales_report.money_close, sales_report.counts_close
        )

        counts = __create_table(
            data=[["Open Money", "Close Money"], [open_counts, close_counts]],
            style=[
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 23),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ],
            rowHeights=[0.5 * inch, 2.75 * inch],
            spaceBefore=30,
        )
        elements.append(counts)

        ## SALES ##
        sales = __create_movements_table("Sales", sales_report.sales)
        elements.append(sales)

        ## RETURNS ##
        returns = __create_movements_table("Returns", sales_report.returns)
        elements.append(returns)

        ## SAVE PDF ##
        pdf.build(elements)

        ## PRINT PDF ##
        self.print_pdf(file_name)

    def print_pdf(self, file_name: str):
        import platform
        import subprocess

        if platform.system() == "Windows":
            subprocess.run(["print", file_name], shell=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["lp", file_name])
        else:  # Linux or others
            subprocess.run(["lp", file_name])
