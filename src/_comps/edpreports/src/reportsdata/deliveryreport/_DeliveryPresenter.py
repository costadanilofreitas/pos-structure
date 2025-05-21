# encoding: utf-8
from unicodedata import normalize

from old_helper import convert_from_utf_to_localtime

from basereport import TableReport, ReportColumnDefinition, SimpleReport
from report import Presenter, Part
from report.command import NewLineCommand, AlignCommand, RepeatCommand
from utils.report_formatters import cut_paper, set_font, bold_on, bold_off, format_cpf_cnpj


class DeliveryPresenter(Presenter):
    def __init__(self, columns):
        self.columns = columns
        
        self.header_column_definition = [
                ReportColumnDefinition(width=8, after_fill_text=': ', fill_with_char='.'),
                ReportColumnDefinition(width=columns - 8)
        ]
        
        self.info_value_column_definition = [
                ReportColumnDefinition(width=columns - 8),
                ReportColumnDefinition(width=8)
        ]
        
        self.delivery_info_column_definition = [
                ReportColumnDefinition(width=13, after_fill_text=': ', fill_with_char='.'),
                ReportColumnDefinition(width=columns - 13)
        ]
        
        self.item_table_column_definitions = [
                ReportColumnDefinition(width=4),
                ReportColumnDefinition(width=columns - 13),
                ReportColumnDefinition(width=9, before_text=" ")
        ]
        
        self.sub_item_table_column_definitions = [
                ReportColumnDefinition(width=6, before_text="  "),
                ReportColumnDefinition(width=columns - 15),
                ReportColumnDefinition(width=9, before_text=" ")
        ]
        
        self.observation_column_definition = [
                ReportColumnDefinition(width=13, after_fill_text=': ', fill_with_char='.'),
                ReportColumnDefinition(width=columns - 13)
        ]
        
        self.full_line_column_definitions = [
                ReportColumnDefinition(width=columns),
                ReportColumnDefinition(width=0)
        ]
    
    def present(self, dto):
        parts = set_font("B")
        parts.extend(self._build_header(dto.header))
        parts.extend(self._build_delivery_information(dto.body))
        parts.extend(self._build_items(dto.body, dto.products))
        parts.extend(self._build_order_values(dto.body))
        parts.extend(self._build_payments(dto.body))
        parts.extend(self._build_observation(dto.body))
        parts.extend(self._build_developer_info())
        
        return SimpleReport(parts, self.columns)
    
    def _build_header(self, header):
        parts = [
                Part(None, [NewLineCommand()]),
                self._get_store_name(header),
                Part(None, [NewLineCommand()]),
                Part(None, [NewLineCommand()])
        ]
        parts.extend(self._get_order_number(header))
        parts.extend(self._get_order_date(header))
        
        return parts
    
    def _build_items(self, body, products):
        items = [
                Part(u"$ITEMS_DELIVERY_REPORT", [AlignCommand(AlignCommand.Alignment.center)]),
                Part(None, [NewLineCommand()]),
                Part(None, [RepeatCommand(self.columns, "#"), NewLineCommand()]),
                TableReport([["$QTY_DELIVERY_REPORT", "$DESCRIPTION_DELIVERY_REPORT", "$VALUE_DELIVERY_REPORT"]],
                            self.item_table_column_definitions),
                Part(None, [RepeatCommand(self.columns, "#"), NewLineCommand()])
        ]
        
        for item in body.items:
            items.extend(self._build_item(item, self.item_table_column_definitions, products, 1))
        
        items.append(Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]))
        
        return items
    
    def _build_item(self, item, column_definition, products, parent_qty):
        items = []
        
        qty = int(item["quantity"]) * parent_qty
        item_quantity = unicode(qty)
        item_part_code = unicode(item["partCode"])
        item_name = self._remove_accents(products[item_part_code] if item_part_code in products else item_part_code)
        item_price = float(item["price"]) * qty
        item_formatted_price = self._format_price(item_price) if item_price > 0 else ''
        item_line = [item_quantity, item_name, item_formatted_price]
        
        if "itemType" not in item or item["itemType"] != "OPTION":
            items.append(TableReport([item_line], column_definition))
            
            if "observation" in item and item["observation"] is not None and item["observation"] != "":
                items.extend([Part("   " + item[u"observation"]), Part(None, [NewLineCommand()])])
        
        if "parts" in item:
            for sub_item in item["parts"]:
                items.extend(self._build_item(sub_item, self.sub_item_table_column_definitions, products, qty))
        
        return items
    
    def _build_order_values(self, body):
        values = []
        
        values.extend(self._format_line("$TOTAL_ITEMS_DELIVERY_REPORT",
                                        self._format_price(float(body.sub_total_price)),
                                        self.info_value_column_definition))
        
        delivery_fee = float(body.delivery_fee)
        if delivery_fee > 0:
            values.extend(self._format_line("$DELIVERY_FEE_DELIVERY_REPORT",
                                            self._format_price(delivery_fee),
                                            self.info_value_column_definition))
        
        if body.vouchers:
            values.append(Part(None, [NewLineCommand()]))
            for key, value in body.vouchers.items():
                if float(value) > 0:
                    values.extend(self._format_line("$" + key + "_DISCOUNT_DELIVERY_REPORT",
                                                    self._format_price(float(value)),
                                                    self.info_value_column_definition))
            values.append(Part(None, [NewLineCommand()]))
        
        values.extend(self._format_line("$TOTAL_DELIVERY_REPORT",
                                        self._format_price(float(body.total_price)),
                                        self.info_value_column_definition))
        values.append(Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]))
        
        return values
    
    def _build_payments(self, body):
        tenders = [
                Part(None, [NewLineCommand()]),
                Part("$PAYMENT_DELIVERY_REPORT", [AlignCommand(AlignCommand.Alignment.center)]),
                Part(None, [NewLineCommand()]),
                Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()])
        ]
        
        for tender in body.tenders:
            tenders.extend(self._format_line(tender["type"],
                                             self._format_price(float(tender["value"])),
                                             self.info_value_column_definition))
        
        tenders.append(Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]))
        
        return tenders
    
    def _build_delivery_information(self, body):
        delivery_information = [
                Part(None, [NewLineCommand()]),
                Part("$INFORMATION_DELIVERY_REPORT", [AlignCommand(AlignCommand.Alignment.center)]),
                Part(None, [NewLineCommand()]),
                Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()])
        ]
        
        delivery_information.extend(self._format_line("$CUSTOMER_NAME_DELIVERY_REPORT",
                                                      body.customer_name,
                                                      self.delivery_info_column_definition))
        delivery_information.extend(self._format_line("$PHONE_DELIVERY_REPORT",
                                                      body.customer_phone,
                                                      self.delivery_info_column_definition))
        delivery_information.extend(self._format_line("$ADDRESS_DELIVERY_REPORT",
                                                      body.address,
                                                      self.delivery_info_column_definition))
        
        delivery_information.extend(self._format_line("$COMPLEMENT_DELIVERY_REPORT",
                                                      body.address_complement,
                                                      self.delivery_info_column_definition))
        
        delivery_information.extend(self._format_line("$NEIGHBORHOOD_DELIVERY_REPORT",
                                                      body.address_neighborhood,
                                                      self.delivery_info_column_definition))
        delivery_information.extend(self._format_line("$CITY_DELIVERY_REPORT",
                                                      body.city,
                                                      self.delivery_info_column_definition))
        delivery_information.extend(self._format_line("$POSTAL_CODE_DELIVERY_REPORT",
                                                      body.postal_code,
                                                      self.delivery_info_column_definition))
        
        delivery_information.extend([
                Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
                Part(None, [NewLineCommand()])
        ])
        
        return delivery_information
    
    def _build_observation(self, body):
        if not body.observation and not body.customer_doc:
            return []
        
        observations = [
                Part(None, [NewLineCommand()]),
                Part("$OBSERVATION_DELIVERY_REPORT", [AlignCommand(AlignCommand.Alignment.center)]),
                Part(None, [NewLineCommand()]),
                Part(None, [RepeatCommand(self.columns, "-")]),
                Part(None, [NewLineCommand()])
        ]
        
        if body.observation:
            for observation in body.observation.split(";"):
                observations.extend(self._format_line('', observation.strip(), self.full_line_column_definitions))
        
        if body.customer_doc:
            observations.extend([Part(None, [NewLineCommand()])])
            observations.extend(self._format_line("$DOCUMENT_DELIVERY_REPORT",
                                                  format_cpf_cnpj(body.customer_doc),
                                                  self.observation_column_definition))
        
        observations.append(Part(None, [RepeatCommand(self.columns, "-")]))
        return observations
    
    @staticmethod
    def _build_developer_info():
        developer_info = [
                Part(None, [NewLineCommand()]),
                Part(None, [NewLineCommand()]),
                Part("$DEVELOPER_DELIVERY_REPORT", [AlignCommand(AlignCommand.Alignment.center)]),
                Part(None, [NewLineCommand()]),
                Part("$DEVELOPER_WEB_SITE_DELIVERY_REPORT", [AlignCommand(AlignCommand.Alignment.center)]),
                Part(None, [NewLineCommand()]),
                Part(None, [NewLineCommand()]),
                Part(None, [NewLineCommand()]),
                Part(None, [NewLineCommand()])
        ]
        
        return developer_info
    
    def _format_line(self, title, text, definition):
        if not text:
            return []
        
        lines = []
        text_width = definition[1].width
        current_string_start = 0
        current_string_end = text_width
        
        while not lines or len(text) > current_string_end:
            if title and current_string_start == 0:
                lines.append(TableReport([[title, text[:current_string_end]]], definition))
            else:
                current_string_end += self.columns
                
                lines.append(TableReport([[text[current_string_start:current_string_end]]],
                                         [ReportColumnDefinition(width=self.columns)]))
            
            current_string_start = current_string_end
        
        return lines
    
    @staticmethod
    def _get_store_name(header):
        return Part(header.store_name.upper(), [AlignCommand(AlignCommand.Alignment.center)])
    
    def _get_order_number(self, header):
        return self._format_line("$ORDER_DELIVERY_REPORT", header.order_number, self.header_column_definition)
    
    def _get_order_date(self, header):
        created_at = convert_from_utf_to_localtime(header.order_date).strftime("%d/%m/%Y %H:%M:%S")
        return self._format_line("$DATE_DELIVERY_REPORT", created_at, self.header_column_definition)
    
    @staticmethod
    def _format_price(price):
        formatted_value = '{:8,.2f}'.format(price)
        return formatted_value
    
    @staticmethod
    def _remove_accents(text):
        return normalize('NFKD', unicode(text.decode('utf8'))).encode('ascii', 'ignore')
