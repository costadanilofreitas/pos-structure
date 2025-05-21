from typing import List  # noqa

from basereport import TableReport, ReportColumnDefinition, AlignTypes
from report import Part
from report.command import RepeatCommand, AlignCommand, FontCommand
from ._ReportBuilder import ReportBuilder
from ..dto import TableReportBodyDto, TableReportOrderDto, TableReportSaleLineDto


class TableReportBody(ReportBuilder):

    def __init__(self, table_report_body_dto, print_by, hide_unpriced_items):
        # type: (TableReportBodyDto, str, bool) -> None
        self.table_report_body_dto = table_report_body_dto
        self.print_by = print_by
        self.hide_unpriced_items = hide_unpriced_items

    def generate(self):
        # type: () -> List[TableReport]

        lines = []
        table_report_order_dto = self.table_report_body_dto.orders

        self \
            ._configure_font(lines) \
            ._generate_items_description(lines) \
            ._repeat_of_equals_symbol_line(lines) \
            ._generate_order(lines,
                             table_report_order_dto,
                             self.table_report_body_dto.tip,
                             self.table_report_body_dto.discount_amount,
                             self.table_report_body_dto.sub_total_amount) \
            ._repeat_of_equals_symbol_line(lines) \
            ._generate_sub_total_summary(lines,
                                         self.table_report_body_dto.sub_total_amount,
                                         self.table_report_body_dto.tip,
                                         self.table_report_body_dto.discount_amount) \
            ._generate_total_summary(lines,
                                     self.table_report_body_dto.total_amount) \
            ._repeat_of_equals_symbol_line(lines) \
            ._generate_total_division_sugestion(lines,
                                                self.table_report_body_dto.total_amount,
                                                self.table_report_body_dto.service_seats) \
            ._generate_customer_doc_field(lines) \
            ._repeat_of_under_symbol_line(lines) \
            ._a_new_empty_line(lines) \
            ._generate_footer(lines)

        return lines

    def _generate_order(self, lines, table_report_order_dto, tip_amount, discount_amount, sub_total_amount):
        # type: (List, List[TableReportOrderDto], float, float, float) -> TableReportBody
        grouped_sale_lines = self._get_grouped_sale_lines(table_report_order_dto)

        if self.print_by == "SEATS" and len(grouped_sale_lines) > 1:
            lines.extend(self._generate_orders_split_by_seats_from_sale_lines_with_tab_on_modifiers(grouped_sale_lines,
                                                                                                    tip_amount,
                                                                                                    discount_amount,
                                                                                                    sub_total_amount))
        else:
            for order in table_report_order_dto:
                lines.extend(self._generate_order_without_split_seats(order))
            lines.extend([a_new_line()])

        return self

    @staticmethod
    def _get_grouped_sale_lines(table_report_order_dto):
        grouped_sale_lines = {}
        preceding_removed_combo = False
        for order in table_report_order_dto:
            for sale_line in order.sales_line_list:
                if sale_line.item_type == "COUPON":
                    continue

                if sale_line.item_type == "COMBO":
                    preceding_removed_combo = False

                if preceding_removed_combo:
                    continue

                if sale_line.item_type == "COMBO" and sale_line.qty == 0:
                    preceding_removed_combo = True
                    continue

                seat = "$TABLE" if sale_line.seat == 0 else sale_line.seat

                if seat not in grouped_sale_lines:
                    grouped_sale_lines[seat] = [sale_line]
                else:
                    grouped_sale_lines[seat].append(sale_line)
        return grouped_sale_lines

    def _generate_order_without_split_seats(self, table_report_order_dto):
        # type: (TableReportOrderDto) -> List

        lines = []

        order_items_lines = self._build_product_lines(table_report_order_dto.sales_line_list)

        order_lines = TableReport(lines=order_items_lines, column_definitions=a_sub_total_summary_column_definition())
        lines.extend([order_lines])

        return lines

    def _generate_orders_split_by_seats_from_sale_lines_with_tab_on_modifiers(self,
                                                                              grouped_sale_lines,
                                                                              tip_amount,
                                                                              discount_amount,
                                                                              sub_total_amount):
        # type: (dict, float, float, float) -> List

        discount_percentage = self._get_percentage(discount_amount, sub_total_amount)
        tip_percentage = self._get_percentage(tip_amount, sub_total_amount)

        lines = []
        for index, seat in enumerate(sorted(grouped_sale_lines)):
            if index != 0:
                lines.append(Part(commands=[RepeatCommand(38, "-")]))
                lines.append(a_new_line())

            seat_sub_total = sum([float(x.price) if x.price and x.qty != 0 else 0.0 for x in grouped_sale_lines[seat]])
            seat_discount = round((discount_percentage * seat_sub_total) / 100, 2)
            seat_tip = round((tip_percentage * seat_sub_total) / 100, 2)
            seat_total = seat_sub_total - seat_discount + seat_tip

            seat_descr = seat if seat == "$TABLE" else "$SEAT_NUMBER {}".format(seat)
            seat_title = [
                [seat_descr, ""]
            ]
            lines.append(TableReport(lines=seat_title, column_definitions=a_total_summary_column_definitions()))
            lines.append(a_new_line())

            seat_details = []
            if seat_discount > 0:
                seat_details.append(["$DISCOUNTS", "#NUMBER({})".format(seat_discount)])
            if seat_tip > 0:
                seat_details.append(["$TIP", "#NUMBER({})".format(seat_tip)])

            seat_details.append(["$TOTAL", "#NUMBER({})".format(seat_total)])

            order_items = self._build_product_lines(grouped_sale_lines[seat])
            order_lines = TableReport(lines=order_items, column_definitions=a_sub_total_summary_column_definition())
            lines.append(order_lines)
            lines.append(a_new_line())

            subtotal = [["$SUBTOTAL", "#NUMBER({})".format(seat_sub_total)]]
            lines.append(TableReport(lines=subtotal, column_definitions=a_total_detail_summary_column_definition()))
            lines.append(TableReport(lines=seat_details, column_definitions=a_total_detail_summary_column_definition()))

        return lines

    @staticmethod
    def _get_percentage(amount, sub_total_amount):
        if amount > 0:
            percentage = round((amount * 100) / sub_total_amount, 2)
        else:
            percentage = 0
        return percentage

    def _build_product_lines(self, sales_line_list):
        # type: (List[TableReportSaleLineDto]) -> List
        if self.hide_unpriced_items:
            sales_line_list = self._remove_unpriced_items(sales_line_list)

        order_items_lines = []
        option_level = None
        for item in sales_line_list:
            if item.item_type in [None, "", "COUPON", "OPTION"]:
                option_level = item.level if item.item_type == "OPTION" else None
                continue

            if item.qty == 0 and (item.default_qty == 0 or item.qty < item.default_qty):
                option_level = None
                continue

            if item.level == 0:
                option_level = None

            item_price = item.price or 0
            item_price = "#NUMBER({})".format(item_price) if item_price else ""

            indentation = " " * ((option_level or item.level) + 1)

            comment_description = ""
            if item.comment and item.comment.startswith("["):
                comment_description = "$" + item.comment.replace("[", "").replace("]", "").upper() + " "

            product_description = comment_description + item.product_name
            line_rjust = len(product_description) + len(indentation)
            description = product_description.rjust(line_rjust)
            qty_description = "{:.2f}".format(item.qty)
            order_items_lines.append([qty_description, description, item_price])

            if item.level <= option_level:
                option_level = None

        return order_items_lines

    @staticmethod
    def _remove_unpriced_items(sales_line_list):
        reduce_next_level = False
        removed_level = None
        lines_to_remove = []
        for line in sales_line_list:
            if line.price == 0:
                reduce_next_level = True
                removed_level = line.level
                lines_to_remove.append(line)
            else:
                if reduce_next_level and line.level > removed_level:
                    line.level -= 1
                elif line.level <= removed_level:
                    reduce_next_level = False
        for line in lines_to_remove:
            sales_line_list.remove(line)

        return sales_line_list

    def _generate_sub_total_summary(self, lines, sub_total_amount, tip_amount, discounts_amount):
        # type: (List, float, float, float) -> TableReportBody
        total_summary_column_definitions = a_total_summary_column_definitions()

        sub_total_lines = [["$SUBTOTAL", "#NUMBER({})".format(sub_total_amount)]]

        if discounts_amount > 0:
            sub_total_lines.append(["$DISCOUNTS", "#NUMBER({})".format(discounts_amount)])
        if tip_amount > 0:
            sub_total_lines.append(["$SUGGESTED_TIP", "#NUMBER({})".format(tip_amount)])

        lines.extend(
            [TableReport(lines=sub_total_lines, column_definitions=total_summary_column_definitions), a_new_line()])
        return self

    def _generate_total_summary(self, lines, total_amount):
        # type: (List, float) -> TableReportBody

        total_summary_column_definitions = a_total_summary_column_definitions()

        sub_total_lines = [
            ["$TOTAL", "#NUMBER({})".format(total_amount)]
        ]
        lines.extend([TableReport(lines=sub_total_lines, column_definitions=total_summary_column_definitions)])
        return self

    def _generate_total_division_sugestion(self, lines, total_amount, service_seats):
        # type: (List, float, int) -> TableReportBody

        if service_seats > 1:
            division_amount = total_amount / service_seats
            sub_total_lines = [
                ["$DIVISION_SUGESTION_FOR {}".format(service_seats), "#NUMBER({})".format(division_amount)]]

            lines.extend(
                [TableReport(lines=sub_total_lines, column_definitions=a_total_division_sugestion_definitions()),
                 a_new_line()
                 ])
        return self

    def _generate_customer_doc_field(self, lines):
        # type: (List) -> TableReportBody

        total_division_sugestion_definitions = a_customer_doc_field()

        sub_total_lines = [["$TYPE_YOUR_DOC_NUM"]]
        lines.extend(
            [TableReport(lines=sub_total_lines, column_definitions=total_division_sugestion_definitions),
             a_new_line()
             ])
        return self

    def _generate_footer(self, lines):
        # type: (List) -> TableReportBody
        lines.extend([
            Part("$THANK_YOU_FOR_YOUR_PREFERENCE", [AlignCommand(AlignCommand.Alignment.center)]), a_new_line(),
            Part("$SERVICE_TAX_IS_NOT_MANDATORY", [AlignCommand(AlignCommand.Alignment.center)]), a_new_line(),
            a_new_line()
        ])
        return self

    def _generate_items_description(self, lines):
        # type: (List[TableReport]) -> TableReportBody

        items_description = TableReport(
            lines=[["$QTY", "$ITEM", "#CURRENCY_SYMBOL()"]],
            column_definitions=a_item_column_definition())

        lines.append(items_description)
        return self

    def _configure_font(self, lines):
        # type: (List[TableReport]) -> TableReportBody
        lines.append(Part(commands=[FontCommand(FontCommand.Font.A)]))

        return self

    def _repeat_of_equals_symbol_line(self, lines):
        # type: (List) -> TableReportBody
        repeat_symbol = [Part(commands=[RepeatCommand(38, "=")]), a_new_line()]
        lines.extend(repeat_symbol)

        return self

    def _repeat_of_under_symbol_line(self, lines):
        # type: (List) -> TableReportBody
        repeat_symbol = [Part(commands=[RepeatCommand(38, "_")]), a_new_line()]
        lines.extend(repeat_symbol)

        return self

    def _a_new_empty_line(self, lines):
        # type: (List) -> TableReportBody
        lines.extend([a_new_line()])

        return self


def a_new_line():
    return Part("\n")


def a_item_column_definition():
    return [
        ReportColumnDefinition(width=5,
                               before_text="",
                               after_text="",
                               after_fill_text="",
                               align=AlignTypes.LEFT),
        ReportColumnDefinition(width=25,
                               fill_with_char=" ",
                               before_text="  ",
                               align=AlignTypes.LEFT),
        ReportColumnDefinition(width=8,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.RIGHT)

    ]


def a_sub_total_summary_column_definition():
    return [
        ReportColumnDefinition(width=5,
                               before_text="",
                               after_text="",
                               after_fill_text="",
                               align=AlignTypes.CENTER),
        ReportColumnDefinition(width=25,
                               fill_with_char=" ",
                               before_text=" ",
                               align=AlignTypes.LEFT),
        ReportColumnDefinition(width=8,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.RIGHT)

    ]


def a_total_detail_summary_column_definition():
    return [
        ReportColumnDefinition(width=25,
                               fill_with_char=" ",
                               before_text=" ",
                               align=AlignTypes.RIGHT),
        ReportColumnDefinition(width=13,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.RIGHT)

    ]


def a_total_summary_column_definitions():
    return [
        ReportColumnDefinition(width=25,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.LEFT),
        ReportColumnDefinition(width=13,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.RIGHT)

    ]


def a_total_division_sugestion_definitions():
    return [
        ReportColumnDefinition(width=25,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.LEFT),
        ReportColumnDefinition(width=13,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.RIGHT)

    ]


def a_customer_doc_field():
    return [
        ReportColumnDefinition(width=25,
                               fill_with_char=" ",
                               before_text=" ",
                               align=AlignTypes.CENTER),
    ]
