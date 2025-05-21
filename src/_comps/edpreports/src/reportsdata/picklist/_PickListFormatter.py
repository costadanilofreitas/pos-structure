# encoding: utf-8
from commons.dto import AlignTypes, ReportColumnDefinition
from commons.report import Formatter
from commons.util import TableReport
from commons.util import EscPosQrCodeGenerator  # noqa
from reports_app.picklist.dto import PickListDto, PickListItem  # noqa

ESC = b'\x1b'
TXT_BOLD_OFF = ESC + b'\x45\x00'  # Bold font OFF
TXT_BOLD_ON = ESC + b'\x45\x01'  # Bold font ON
TXT_ALIGN_CT = ESC + b'\x61\x01'  # Centering
TXT_ALIGN_LT = ESC + b'\x61\x00'  # Left justification


class PickListFormatter(Formatter):

    def __init__(self, formatter_type, qrcode_string_before, qrcode_string_after, show_qrcode):
        super(PickListFormatter, self).__init__()
        self.formatter_type = formatter_type
        self.qrcode_string_before = qrcode_string_before
        self.qrcode_string_after = qrcode_string_after
        self.show_qrcode = show_qrcode
        self.translated_messages = {}

    def format_report(self, pick_list_dto, translator):
        # type: (PickListDto) -> str
        self.translated_messages = translator.translate_labels(["$STORE",
                                                                  "$DATE_HOUR",
                                                                  "$ORDER_NUMBER",
                                                                  "$CUSTOMER_NAME",
                                                                  "$EXTRA",
                                                                  "$WITHOUT",
                                                                  "$DRIVE_THRU",
                                                                  "$TAKE_OUT",
                                                                  "$TOTEM",
                                                                  "$DELIVERY",
                                                                  "$ADDRESS_CAP",
                                                                  "$REFERENCE",
                                                                  "$NEIGHBORHOOD",
                                                                  "$ZIPCODE",
                                                                  "$CITY",
                                                                  "$STATE",
                                                                  "$PARTNER",
                                                                  "$PARTNER_NUMBER"], pick_list_dto.pos_id)

        report = self._validate_and_create_header_and_body(pick_list_dto)
        report_bytes = report.encode("utf-8")
        report_bytes = self._append_qrcode(pick_list_dto, report_bytes)
        return report_bytes

    def _validate_and_create_header_and_body(self, pick_list_dto):
        self._validate_header_body_none(pick_list_dto)
        report = self._append_header(pick_list_dto)
        report = self._choose_type_body_format(pick_list_dto, report)
        return report

    def _append_qrcode(self, pick_list_dto, report_bytes):
        if self.show_qrcode:
            report_bytes += ("%(TXT_ALIGN_CT)s" % self._join(globals(), locals()))
            report_bytes += EscPosQrCodeGenerator.generate_qr_code(self.qrcode_string_before +
                                                                   str(pick_list_dto.pick_list_header.order_id).zfill(8) +
                                                                   self.qrcode_string_after)
            report_bytes += ("%(TXT_ALIGN_LT)s" % self._join(globals(), locals()))
            report_bytes = self._add_final_line(report_bytes)

        return report_bytes

    def _add_final_line(self, report_bytes):
        report_lines = []
        report_lines.append([ReportColumnDefinition(fill_with_char=' ')])
        report_lines.append([ReportColumnDefinition(fill_with_char='=')])
        table_formatter = TableReport([ReportColumnDefinition(width=38)])
        report_bytes += table_formatter.format(report_lines)
        return report_bytes

    def _choose_type_body_format(self, pick_list_dto, report):
        if str(self.formatter_type) == 'normal':
            report += self._append_body(pick_list_dto)
        else:
            report += self._append_body_grouped(pick_list_dto)
        return report

    def _validate_header_body_none(self, pick_list_dto):
        if pick_list_dto.pick_list_header is None:
            raise PickListFormatter.InvalidDto(PickListFormatter.InvalidDto.HeaderIsNone)
        if pick_list_dto.pick_list_body is None:
            raise PickListFormatter.InvalidDto(PickListFormatter.InvalidDto.BodyIsNone)

    def _append_header(self, pick_list_dto):
        # type: (PickListDto) -> str
        report_lines = []

        self._append_data_header(pick_list_dto, report_lines)

        table_formatter = TableReport(lines=report_lines,
                                      column_definitions=[
            ReportColumnDefinition(width=12, fill_with_char='.'),
            ReportColumnDefinition(width=26, before_text=': ')
        ])

        return table_formatter.generate_parts()

    def _append_data_header(self, pick_list_dto, report_lines):
        self._append_line_separator(report_lines)
        self._append_title(report_lines, pick_list_dto)
        self._append_current_date(report_lines, pick_list_dto.pick_list_header)
        self._append_order_id_and_store(report_lines, pick_list_dto.pick_list_header)
        self._append_client_name(report_lines, pick_list_dto.pick_list_header)
        self._append_data_address(report_lines, pick_list_dto, pick_list_dto.pick_list_header)

    @staticmethod
    def _append_line_separator(report_lines):
        report_lines.append([ReportColumnDefinition(
            fill_with_char='='
        )])

    def _append_title(self, report_lines, pick_list_dto):
        title = self._get_title(pick_list_dto)
        report_lines.append([ReportColumnDefinition(
            text="(" + self.translated_messages[title].upper() + ")",
            align=AlignTypes.CENTER
        )])

    def _get_title(self, pick_list_dto):
        title = "$STORE"
        if pick_list_dto.pod_type == "DT":
            title = "$DRIVE_THRU".upper()
        if pick_list_dto.pod_type == "TT":
            title = "$TOTEM"
        if pick_list_dto.pod_type == "DL":
            title = "$DELIVERY"
        return title

    def _append_data_address(self, report_lines, pick_list_dto, pick_list_header):

        if pick_list_dto.pod_type == "DL":

            list_keys_to_sort = [self.translated_messages["$ADDRESS_CAP"],
                                 self.translated_messages["$REFERENCE"],
                                 self.translated_messages["$NEIGHBORHOOD"],
                                 self.translated_messages["$ZIPCODE"],
                                 self.translated_messages["$CITY"],
                                 self.translated_messages["$STATE"],
                                 self.translated_messages["$PARTNER"],
                                 self.translated_messages["$PARTNER_NUMBER"]]

            dict_address_values = {self.translated_messages["$ADDRESS_CAP"]: "##ADDRESS##",
                                   self.translated_messages["$REFERENCE"]: "##referencia com mais de trinta e oito"
                                                                           " caracteres para teste e com mais "
                                                                           "de duas linhas##",
                                   self.translated_messages["$NEIGHBORHOOD"]: "##NEIGHBORHOOD##",
                                   self.translated_messages["$ZIPCODE"]: "##ZIPCODE##",
                                   self.translated_messages["$CITY"]: "##CITY##",
                                   self.translated_messages["$STATE"]: "##STATE##",
                                   self.translated_messages["$PARTNER"]: "##PARTNER##",
                                   self.translated_messages["$PARTNER_NUMBER"]: "##PARTNER_NUMBER##"}
            for key in list_keys_to_sort:
                self._append_lines_address(dict_address_values, key, report_lines)

    def _append_lines_address(self, dict_address_values, key, report_lines):
        size_text = 25
        parts = len(dict_address_values.get(key)) / float(size_text)
        report_lines.append([key, dict_address_values.get(key)[:size_text]])
        if parts > 1:
            self._line_break_address(dict_address_values, key, parts, report_lines, size_text)

    def _line_break_address(self, dict_address_values, key, parts, report_lines, size_text):
        for part in range(int(parts) - 1):
            report_lines.append(
                [ReportColumnDefinition(
                    text=dict_address_values.get(key)[25 + (size_text * part):(size_text * (part + 1)) + 38],
                    align=AlignTypes.LEFT,
                    width=38)])
            size_text = 38

    def _append_current_date(self, report_lines, pick_list_header_dto):
        report_lines.append([self.translated_messages["$DATE_HOUR"],
                             pick_list_header_dto.date.strftime("%d/%m/%Y %H:%M:%S")])

    def _append_order_id_and_store(self, report_lines, pick_list_header_dto):
        report_lines.append([self.translated_messages["$ORDER_NUMBER"],
                             str(pick_list_header_dto.order_id) + " / " + str(pick_list_header_dto.store)])

    def _append_client_name(self, report_lines, pick_list_header_dto):
        if pick_list_header_dto.client_name is None:
            pick_list_header_dto.client_name = ""

        report_lines.append([self.translated_messages["$CUSTOMER_NAME"],
                             pick_list_header_dto.client_name])

    def _append_body(self, pick_list_dto):
        # type: (PickListDto) -> str
        report_lines = []
        self._append_data_body(pick_list_dto, report_lines)

        table_formatter = TableReport([
            ReportColumnDefinition(width=38, fill_with_char=' ')
        ])

        return table_formatter.format(report_lines)

    def _append_body_grouped(self, pick_list_dto):
        # type: (PickListDto) -> str
        report_lines = []
        self._append_init_body(report_lines, pick_list_dto)
        self._create_data_to_format_grouped(pick_list_dto, report_lines)
        self._append_end_body(report_lines, pick_list_dto)

        table_formatter = TableReport([ReportColumnDefinition(width=38, fill_with_char=' ')])
        return table_formatter.format(report_lines)

    def _append_data_body(self, pick_list_dto, report_lines):
        self._append_init_body(report_lines, pick_list_dto)
        for pick_list_item in pick_list_dto.pick_list_body.pick_list_items:
            text_space = ""
            self._append_item_info(report_lines, pick_list_item, text_space, True, None, False)
        self._append_end_body(report_lines, pick_list_dto)

    def _append_init_body(self, report_lines, pick_list_dto):
        self._append_line_separator(report_lines)
        if pick_list_dto.pod_type == "DT" or pick_list_dto.pod_type == "DL":
            self._append_pod_type(report_lines, pick_list_dto.pod_type)
        elif pick_list_dto.sale_type != "EAT_IN":
            self._append_sale_type(report_lines, pick_list_dto.sale_type)
        self._append_empty_line(report_lines)

    def _append_end_body(self, report_lines, pick_list_dto):
        self._append_empty_line(report_lines)
        if pick_list_dto.pod_type == "DT" or pick_list_dto.pod_type == "DL":
            self._append_pod_type(report_lines, pick_list_dto.pod_type)
        elif pick_list_dto.sale_type != "EAT_IN":
            self._append_sale_type(report_lines, pick_list_dto.sale_type)
        self._append_empty_line(report_lines)

    def _append_pod_type(self, report_lines, pod_type):
        if pod_type == "DT":
            report_lines.append([ReportColumnDefinition(
                text=self.translated_messages["$DRIVE_THRU"],
                align=AlignTypes.CENTER,
                fill_with_char="*"
            )])
        if pod_type == "DL":
            report_lines.append([ReportColumnDefinition(
                text=" " + self.translated_messages["$DELIVERY"].upper() + " ",
                align=AlignTypes.CENTER,
                fill_with_char="*"
            )])

    def _append_sale_type(self, report_lines, sale_type):
        if sale_type == "TAKE_OUT":
            report_lines.append([ReportColumnDefinition(
                text=" " + self.translated_messages["$TAKE_OUT"] + " ",
                align=AlignTypes.CENTER,
                fill_with_char="*"
            )])

    def _create_data_to_format_grouped(self, pick_list_dto, report_lines):
        list_items = []  # type: List[PickListItem]
        list_items_grouped = []
        self._create_list_items(list_items, pick_list_dto.pick_list_body)
        self._create_list_items_grouped(list_items, list_items_grouped)
        self._create_lines_grouped(list_items, list_items_grouped, report_lines)

    def _create_lines_grouped(self, list_items, list_items_grouped, report_lines):
        for j in list_items_grouped:
            qty_item = 0
            self._create_lines_items(j, list_items, qty_item, report_lines)
            self._create_lines_sub_items(j, report_lines)

    def _create_lines_sub_items(self, j, report_lines):
        for sub_item in j.sub_items:
            if int(sub_item.qty) == 0:
                line = self.translated_messages["$WITHOUT"] + " " + sub_item.description
            else:
                line = "{} {} {}".format(str(int(sub_item.qty) - int(sub_item.default_qty)),
                                         self.translated_messages["$EXTRA"],
                                         sub_item.description)
            text = "%(TXT_BOLD_ON)s%(line)s%(TXT_BOLD_OFF)s" % self._join(globals(), locals())
            report_lines.append([ReportColumnDefinition(text=text, before_text="   ")])

    def _create_lines_items(self, j, list_items, qty_item, report_lines):
        for i in list_items:
            if self._compare_item(j, i):
                if int(i.qty) != 0:
                    qty_item = qty_item + int(j.multiplied_qty)
        self._add_text_item(j, qty_item, report_lines)

    def _add_text_item(self, j, qty_item, report_lines):
        if int(j.qty) != 0:
            line = str(qty_item) + " " + j.description
            text = "%(TXT_BOLD_ON)s%(line)s%(TXT_BOLD_OFF)s" % self._join(globals(), locals())
            report_lines.append([ReportColumnDefinition(text=text)])

    def _create_list_items_grouped(self, list_items, list_items_grouped):
        for i in list_items:
            list_items_grouped.append(i)
        for i in range(0, len(list_items)):
            for j in range(i + 1, len(list_items)):
                self._compare_item_and_remove_equal(i, j, list_items, list_items_grouped)

    def _compare_item_and_remove_equal(self, i, j, list_items, list_items_grouped):
        if self._compare_item(list_items[i], list_items[j]):
            if list_items[j] in list_items_grouped:
                if int(list_items[j].qty) == 0:
                    list_items_grouped.remove(list_items[j])
                else:
                    list_items_grouped.remove(list_items[i])

    def _create_list_items(self, list_items, pick_list_body):
        for pick_list_item in pick_list_body.pick_list_items:
            if pick_list_item.item_type == 'COMBO':
                for sub_item in pick_list_item.sub_items:
                    self._append_sub_items(list_items, sub_item)
            else:
                list_items.append(pick_list_item)

    def _append_sub_items(self, list_items, sub_item):
        if sub_item.item_type == 'OPTION':
            for sub_item_option in sub_item.sub_items:
                list_items.append(sub_item_option)
        else:
            list_items.append(sub_item)

    def _compare_item(self, item1, item2):
        if item1.description == item2.description and len(item1.sub_items) == len(item2.sub_items):
            if len(item1.sub_items) == 0:
                return True
            return self._compare_sub_items(item1.sub_items, item2.sub_items)
        else:
            return False

    def _compare_sub_items(self, sub_items1, sub_items2):
        for i in range(0, len(sub_items1)):
            is_equal = False
            for j in range(0, len(sub_items2)):
                if sub_items1[i].description == sub_items2[j].description and sub_items1[i].qty == sub_items2[j].qty:
                    is_equal = True
                    break
        return is_equal

    def _append_item_info(self, report_lines, pick_list_item, text_space, first, default_qty, is_option_sub_item):
        text = ""
        default_qty, is_option_sub_item, text_space = self._validate_is_option_and_create_text(default_qty, first,
                                                                                               is_option_sub_item,
                                                                                               pick_list_item,
                                                                                               report_lines, text,
                                                                                               text_space)

        for pick_list_item in pick_list_item.sub_items:
            self._append_item_info(report_lines, pick_list_item, text_space, False, default_qty, is_option_sub_item)

    def _validate_is_option_and_create_text(self, default_qty, first, is_option_sub_item, pick_list_item, report_lines,
                                            text, text_space):
        if pick_list_item.item_type == "OPTION":
            default_qty = int(pick_list_item.qty) - int(pick_list_item.default_qty)
            is_option_sub_item = True
        elif (is_option_sub_item and int(pick_list_item.qty) != 0) or not is_option_sub_item:
                default_qty, text_space = self._create_text_and_append_lines(default_qty,
                                                                             first,
                                                                             pick_list_item,
                                                                             report_lines,
                                                                             text,
                                                                             text_space)
        return default_qty, is_option_sub_item, text_space

    def _join(self, dic1, dic2):
        d = dict(dic1)
        d.update(dic2)
        return d

    def _create_text_and_append_lines(self, default_qty, first, pick_list_item, report_lines, text, text_space):
        default_qty, text = self._create_line(default_qty, first, pick_list_item, text)
        report_lines.append([ReportColumnDefinition(text=text, before_text=text_space)])
        text_space += "   "
        return default_qty, text_space

    def _create_line(self, default_qty, first, pick_list_item, text):
        if pick_list_item.item_type == "COMBO" or first:
            line = str(pick_list_item.qty) + " " + pick_list_item.description
            text = "%(TXT_BOLD_ON)s%(line)s%(TXT_BOLD_OFF)s" % self._join(globals(), locals())
        else:
            default_qty, qty_items = self._get_default_qty(default_qty, pick_list_item)
            text = self._add_description(pick_list_item, qty_items, text)
        return default_qty, text

    def _add_description(self, pick_list_item, qty_items, text):
        if qty_items > 0:
            text = self._add_extra_items(pick_list_item, qty_items, text)
        elif qty_items < 0:
            text = self._remove_items(pick_list_item, text)
        else:
            text += pick_list_item.description
        return text

    def _add_extra_items(self, pick_list_item, qty_items, text):
        x = 0
        while x < qty_items:
            text += self.translated_messages["$EXTRA"] + " " + pick_list_item.description
            x = x + 1
        return text

    def _remove_items(self, pick_list_item, text):
        text += self.translated_messages["$WITHOUT"] + " " + pick_list_item.description
        return text

    def _get_default_qty(self, default_qty, pick_list_item):
        if default_qty is None:
            qty_items = int(pick_list_item.qty) - int(pick_list_item.default_qty)
        else:
            qty_items = default_qty
            default_qty = None
        return default_qty, qty_items

    @staticmethod
    def _append_empty_line(report_lines):
        report_lines.append([ReportColumnDefinition(fill_with_char=' ')])

    class InvalidDto(Exception):
        HeaderIsNone = "Header is None"
        BodyIsNone = "Body is None"

        def __init__(self, message):
            super(PickListFormatter.InvalidDto, self).__init__(message)
