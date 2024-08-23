from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
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

    def generate_report(self, sales_report: SalesReport):
        # Elements container
        elements = []

        # Create PDF
        fie_name = f"sales_report_{sales_report.date}.pdf"
        pdf = SimpleDocTemplate(fie_name, pagesize=letter)

        # Set attributes
        pdf.title = "Daily Sales Report"
        pdf.author = "Diego Balestra"
        pdf.creator = "Scrubs Boutique and More"

        pdf.topMargin = 10
        pdf.bottomMargin = 10
        pdf.leftMargin = 20
        pdf.rightMargin = 20

        ## HEADER ##
        image_w = 330 / 2.5
        image_h = 149 / 2.5
        image = Image("assets/scrubs_logo.png", image_w, image_h)

        title_text = """<font name=Helvetica-Bold color=black size=19>Daily Sales Report</font> <font name=Helvetica color=grey size=8>v8</font><br/>
        <font name=Helvetica color=grey size=12>Scrubs Boutique and More LLC</font>"""
        title_para = Paragraph(title_text)
        header = ParagraphAndImage(title_para, image, ypad=20)
        elements.append(header)

        ## DATA ##
        store_name = sales_report.store.name
        store_open, store_close = sales_report.schedule.working_hours
        working_hours = store_close.hour - store_open.hour
        date = sales_report.date.strftime("%B %d, %Y")

        data = [["Store", "Hours", "Date"], [store_name, working_hours, date]]
        data_style = TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 18),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                ("FONTSIZE", (0, 1), (-1, 1), 14),
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.grey),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
        data_table = Table(
            data,
            style=data_style,
            spaceBefore=75,
            colWidths=[2.5 * inch],
            rowHeights=[0.45 * inch, 0.3 * inch],
        )
        elements.append(data_table)

        ## COUNTS ##
        # Open counts
        o_bills = sales_report.money_open.bills
        o_cents = sales_report.money_open.cents
        o_counts = sales_report.counts_open
        open_counts = [
            ["$100", o_bills["100"], "¢25", o_cents["25"]],
            ["$50", o_bills["50"], "¢10", o_cents["10"]],
            ["$20", o_bills["20"], "¢5", o_cents["5"]],
            ["$10", o_bills["10"], "¢1", o_cents["1"]],
            ["$5", o_bills["5"], "Gift cards", ""],
            ["$2", o_bills["2"], 50, o_counts.gift_cards.fifty],
            ["$1", o_bills["1"], 25, o_counts.gift_cards.t_five],
            ["Littmanns", "", o_counts.littmanns, ""],
            ["Total", "", f"${count_money(o_bills, o_cents)}", ""],
        ]
        counts_style = TableStyle(
            [
                ("SPAN", (2, 4), (-1, 4)),
                ("SPAN", (0, -1), (1, -1)),
                ("SPAN", (2, -1), (-1, -1)),
                ("SPAN", (0, -2), (1, -2)),
                ("SPAN", (-2, -2), (-1, -2)),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, -2), (1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (-2, 0), (-2, -3), "Helvetica-Bold"),
                ("BOX", (2, -5), (-1, -3), 0.5, colors.grey),
                ("LINEABOVE", (2, -4), (-1, -4), 0.5, colors.grey),
                ("TEXTCOLOR", (1, 0), (1, -3), colors.grey),
                ("TEXTCOLOR", (3, 0), (3, -3), colors.grey),
                ("TEXTCOLOR", (2, -2), (2, -1), colors.grey),
            ]
        )
        open_counts_table = Table(open_counts, style=counts_style)

        # Close counts
        money_close = sales_report.money_close
        if money_close:
            c_bills = money_close.bills
            c_cents = money_close.cents
        else:
            c_bills = {}
            c_cents = {}

        c_counts = sales_report.counts_close
        if c_counts:
            fifty = c_counts.gift_cards.fifty
            t_five = c_counts.gift_cards.t_five
            littmanns = c_counts.littmanns
        else:
            fifty = 0
            t_five = 0
            littmanns = 0

        close_counts = [
            ["$100", c_bills.get("100", 0), "¢25", c_cents.get("25", 0)],
            ["$50", c_bills.get("50", 0), "¢10", c_cents.get("10", 0)],
            ["$20", c_bills.get("20", 0), "¢5", c_cents.get("5", 0)],
            ["$10", c_bills.get("10", 0), "¢1", c_cents.get("1", 0)],
            ["$5", c_bills.get("5", 0), "Gift cards", ""],
            ["$2", c_bills.get("2", 0), 50, fifty],
            ["$1", c_bills.get("1", 0), 25, t_five],
            ["Littmanns", "", littmanns, ""],
            ["Total", "", f"${count_money(c_bills, c_cents)}", ""],
        ]
        close_counts_table = Table(close_counts, style=counts_style)

        # Counts
        counts = [
            ["Open Money", "Close Money"],
            [open_counts_table, close_counts_table],
        ]
        counts_style = TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 23),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
        counts_table = Table(
            counts,
            style=counts_style,
            spaceBefore=50,
            rowHeights=[0.5 * inch, 2.75 * inch],
        )
        elements.append(counts_table)

        # Returns
        # Sales

        # Save PDF
        pdf.build(elements)
