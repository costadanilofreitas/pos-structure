# -*- coding: utf-8 -*-
import json
import locale
from datetime import datetime
from xml.etree import cElementTree as eTree

import sysactions
from pos_model import TenderType
from repository import OrderRepository, AccountRepository, TenderRepository, FiscalRepository, PosCtrlRepository, \
    ProductRepository, TableRepository
from sysactions import get_storewide_config
from typing import Dict, List, Optional, Tuple, Union

from .model import Order, TotalTender, Transfer


class CashReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"
    TypeXml = "Xml"

    def __init__(self, order_repository, account_repository, tender_repository, fiscal_repository, pos_ctrl_repository, table_repository, product_repository, store_id, delivery_originator_relation=None):
        # type: (OrderRepository, AccountRepository, TenderRepository, FiscalRepository, PosCtrlRepository, TableRepository, ProductRepository, unicode, Union[List[str], None]) -> None
        self.order_repository = order_repository
        self.account_repository = account_repository
        self.tender_repository = tender_repository
        self.fiscal_repository = fiscal_repository
        self.pos_ctrl_repository = pos_ctrl_repository
        self.table_repository = table_repository
        self.product_repository = product_repository
        self.store_id = store_id
        self.delivery_originator_relation = delivery_originator_relation
        self.print_card_brands = get_storewide_config("Store.PrintCardBrands", defval="False").lower() == "true"

        self._format_delivery_originator_relation()

        self.tender_names_dict = {}  # type: Dict[int, unicode]
        for tender_tuple in self.tender_repository.get_tender_names():
            self.tender_names_dict[tender_tuple[0]] = tender_tuple[1]

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

    def _format_delivery_originator_relation(self):
        if self.delivery_originator_relation:
            formatted_delivery_originator_relation = {}
            for relation in self.delivery_originator_relation:
                originator = relation.split("|")[0]
                brand = relation.split("|")[1]
                formatted_delivery_originator_relation[originator] = brand
            self.delivery_originator_relation = formatted_delivery_originator_relation

    def generate_cash_report_by_real_date(self, pos_id, report_pos, initial_date, end_date, operator_id, voided_lines, business_period=None, codigo_centro=None, close_time=None, is_table_service=False, only_body=False, session_id=None, only_payments=False):
        if business_period is None:
            return self._generate_cash_report(self.TypeRealDate, pos_id, report_pos, initial_date, end_date, operator_id, session_id, voided_lines, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)
        else:
            return self._generate_cash_report_json(pos_id, report_pos, initial_date, end_date, operator_id, codigo_centro, close_time, voided_lines)

    def generate_cash_report_by_business_period(self, pos_id, report_pos, initial_date, end_date, operator_id, voided_lines, is_table_service=False, only_body=False, only_payments=False):
        return self._generate_cash_report(self.TypeBusinessPeriod, pos_id, report_pos, initial_date, end_date, operator_id, None, voided_lines, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)

    def generate_cash_report_by_session_id(self, pos_id, session_id, voided_lines, is_table_service=False, only_body=False, only_payments=False):
        return self._generate_cash_report(self.TypeSessionId, pos_id, None, None, None, None, session_id, voided_lines, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)

    def generate_cash_report_by_xml(self, pos_id, initial_date, end_date, is_table_service=False, only_body=False, only_payments=False):
        return self._generate_cash_report(self.TypeXml, pos_id, None, initial_date, end_date, None, None, None, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)

    def _generate_cash_report(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, voided_lines, is_table_service=False, only_body=False, only_payments=False):
        if report_type == self.TypeRealDate:
            paid_orders = self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, operator_id, report_pos, session_id)
            voided_orders = self.order_repository.get_voided_orders_by_real_date(initial_date, end_date, operator_id, report_pos, session_id)
            transfers = self.account_repository.get_transfers_by_real_date(initial_date, end_date, operator_id, report_pos, session_id)
            opened_orders = None
            if is_table_service:
                opened_orders = self.order_repository.get_opened_orders(report_type,
                                                                        initial_date=initial_date,
                                                                        end_date=end_date,
                                                                        operator_id=operator_id)

        elif report_type == self.TypeBusinessPeriod:
            paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
            voided_orders = self.order_repository.get_voided_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
            transfers = self.account_repository.get_transfers_by_business_period(initial_date, end_date, operator_id, report_pos)
            opened_orders = None
            if is_table_service:
                opened_orders = self.order_repository.get_opened_orders(report_type,
                                                                        initial_date=initial_date,
                                                                        end_date=end_date,
                                                                        operator_id=operator_id)

        elif report_type == self.TypeSessionId:
            paid_orders = self.order_repository.get_paid_orders_by_session_id(session_id)
            voided_orders = self.order_repository.get_voided_orders_by_session_id(session_id)
            transfers = self.account_repository.get_transfers_by_session_id(session_id)
            start_index = session_id.find("user=")
            end_index = session_id.find(",", start_index)
            operator_id = session_id[start_index + 5:end_index]
            start_index = session_id.find("period=")
            initial_date = end_date = datetime.strptime(session_id[start_index + 7:], "%Y%m%d")
            opened_orders = None
            if is_table_service:
                opened_orders = self.order_repository.get_opened_orders(report_type,
                                                                        session_id=session_id,
                                                                        operator_id=operator_id)

        else:
            paid_orders = self.order_repository.get_paid_orders_by_xml(initial_date, end_date)
            voided_orders = self.order_repository.get_voided_orders_by_xml(initial_date, end_date)
            transfers = self.account_repository.get_transfers_by_real_date(initial_date, end_date, None, report_pos)
            operator_id = None
            opened_orders = None

        card_brands_payments = self.order_repository.get_payments_by_order(paid_orders)
        payments_by_brand = self.product_repository.populate_card_brands_groups(card_brands_payments)
        tef_card_brands = self._get_tef_card_brands(paid_orders)

        count_pos_error = filter(lambda x: x == "error", paid_orders)
        count_pos_error = len(count_pos_error)

        paid_orders = filter(lambda x: x != "error", paid_orders)
        voided_orders = filter(lambda x: x != "error", voided_orders)

        tables_by_sector = self.table_repository.get_tables_by_sector(paid_orders)
        paid_orders = self._fill_orders_sector(tables_by_sector, paid_orders)
        voided_orders = self._fill_orders_sector(tables_by_sector, voided_orders)

        header = ""
        if not only_body:
            header = self._build_header(report_type, pos_id, report_pos, initial_date, end_date, operator_id, only_payments, count_pos_error)
        if only_payments:
            body = self._build_body_only_with_payments(payments_by_brand, tef_card_brands)
        else:
            body = self._build_body(pos_id, paid_orders, voided_orders, opened_orders, transfers, report_type, voided_lines, payments_by_brand, tef_card_brands, is_table_service, operator_id)
            if is_table_service and report_type not in [self.TypeXml, self.TypeSessionId]:
                average_info = self.table_repository.get_sales_average_info(initial_date, end_date, operator_id)
                table_info = self._build_table_info(average_info, paid_orders)
                body += table_info

        report = header + body

        report_bytes = report.encode("utf-8")

        return report_bytes

    def _get_tef_card_brands(self, paid_orders):
        grouped_card_brands = {}
        brands_descriptions = self.fiscal_repository.get_brands_description()
        tenders = self.order_repository.get_tender_details(paid_orders)
        for tender_id, tender_amount, tender_detail in tenders:
            if int(tender_id) not in [TenderType.credit, TenderType.debit]:
                continue

            detail = json.loads(tender_detail)
            card_brand_id = int(detail['Bandeira'])
            card_brand = brands_descriptions[card_brand_id] if card_brand_id in brands_descriptions else 'OUTROS'
            tender_amount = float(tender_amount)
            tender_id = int(tender_id)
            brand_key = (card_brand, tender_id)
            if brand_key not in grouped_card_brands:
                grouped_card_brands[brand_key] = {}
                grouped_card_brands[brand_key]["tenderId"] = tender_id
                grouped_card_brands[brand_key]["value"] = tender_amount
                grouped_card_brands[brand_key]["quantity"] = 1
            else:
                grouped_card_brands[brand_key]["value"] += tender_amount
                grouped_card_brands[brand_key]["quantity"] += 1

        return grouped_card_brands

    def _build_header(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, only_payments, count_pos_error=0):
        # type: (unicode, int, Optional[unicode], datetime, datetime, unicode, bool, int) -> unicode
        pos_list = "Todos" if report_pos is None else report_pos.zfill(2)
        if report_type == self.TypeRealDate:
            report_type_text = "Data Fiscal"
        elif report_type == self.TypeBusinessPeriod:
            report_type_text = "Dia Negocio"
        elif report_type == self.TypeXml:
            report_type_text = "Arquivo Xml"
        else:
            report_type_text = "Surpresa"
            pos_list = pos_id

        if operator_id != "0" and operator_id is not None:
            operator_name = eTree.XML(sysactions.get_user_information(operator_id)).find(".//user").get("LongName")[:20]
        else:
            operator_name = "Todos"

        if not only_payments:
            report_name = "Relatorio de Vendas"
        else:
            report_name = "Relatorio de Bandeiras"

        header =  u"======================================\n"
        header += u"{0} - {1}".format(report_name, report_type_text).center(38)
        header += u"\n Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u"\n Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        if report_type != self.TypeSessionId:
            header += u" {0:.<13}: {1} - {2}\n".format("Periodo", initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" Operador.....: " + u"{0}\n".format(operator_name[:20])
        temp_pos_list = u" POS incluidos: " + u"{0}".format(pos_list)
        header += temp_pos_list[:38]
        if len(temp_pos_list) > 38:
            header += (u"\n                %s" % temp_pos_list[38:60])
        if len(temp_pos_list) > 66:
            header += (u"\n                %s" % temp_pos_list[60:82])
        header += u"\n"
        if count_pos_error > 0:
            header += u" POS excluidos: " + u"{0}\n".format(count_pos_error)

        header += u"======================================\n"

        return header

    def _build_body(self, pos_id, paid_orders, voided_orders, opened_orders, transfers, report_type, voided_lines, payments_by_brand=None, tef_card_brands=None, is_table_service=False, operator_id=None):
        # type: (int, List[Order], List[Order], List, List[Transfer], unicode, int, Optional[List[Tuple[unicode, int, float, int]]], dict, bool, int) -> unicode

        qty_paid_orders, \
        qty_discount, \
        qty_donation, \
        qty_tip, \
        value_paid_orders, \
        value_discount, \
        value_donation, \
        value_tip = self._get_paid_order_values(paid_orders)

        qty_coupons_voided, \
        qty_lines_voided, \
        qty_orders_voided, \
        qty_total_voided, \
        value_coupons_voided, \
        value_lines_voided, \
        value_orders_voided, \
        value_total_voided = self._get_voided_order_values(voided_lines, voided_orders)

        grouped_paid_orders_by_sector = self._get_grouped_paid_orders_by_sector(paid_orders)

        delivery_paid_orders = filter(lambda x: x.sale_type == 3 and x.delivery_originator, paid_orders)
        qty_delivery_orders, value_delivery_orders = self._get_delivery_orders_values(delivery_paid_orders)
        
        manual_delivery_paid_orders = filter(lambda x: x.sale_type == 3 and not x.delivery_originator, paid_orders)
        qty_manual_delivery_orders, value_manual_delivery_orders = self._get_delivery_orders_values(manual_delivery_paid_orders)
        
        qty_opened_orders = 0
        value_opened_orders = 0
        if is_table_service:
            qty_opened_orders, value_opened_orders = self._get_opened_orders_values(pos_id, opened_orders)

        initial_balance = self._get_initial_balance(is_table_service, transfers)

        body = u"Descricao          Qtd    Total\n"
        body += u"======================================\n"
        if not is_table_service:
            body += u"Balanco Inicial..:        R${0:>10}\n".format(self._str_float(initial_balance))
        total_gross = self._str_float(value_paid_orders + value_discount + value_opened_orders)
        body += u"Venda Bruta......: [{0:>4}] R${1:>10}\n".format(qty_paid_orders + qty_opened_orders, total_gross)
        body += u"Descontos........: [{0:>4}] R${1:>10}\n".format(qty_discount, self._str_float(value_discount))
        total_qty = self._str_float(value_paid_orders + value_opened_orders)
        body += u"Venda Acumulada..: [{0:>4}] R${1:>10}\n".format(qty_paid_orders + qty_opened_orders, total_qty)

        if not (qty_opened_orders != 0 and value_opened_orders == 0) and is_table_service:
            body += u"Venda Aberta.....: [{0:>4}] R${1:>10}\n".format(qty_opened_orders, self._str_float(value_opened_orders))
        body += u"Venda Faturada...: [{0:>4}] R${1:>10}\n".format(qty_paid_orders, self._str_float(value_paid_orders))

        for sector in sorted(grouped_paid_orders_by_sector, key=lambda x: grouped_paid_orders_by_sector[x]['value'], reverse=True):
            quantity = grouped_paid_orders_by_sector[sector]['quantity']
            value = self._str_float(grouped_paid_orders_by_sector[sector]['value'])
            body += u"  {0:.<15}: [{1:>4}] R${2:>10}\n".format(sector, quantity, value)

        if qty_delivery_orders > 0:
            body += u"  Delivery.......: [{0:>4}] R${1:>10}\n".format(qty_delivery_orders,
                                                                      self._str_float(value_delivery_orders))

            self._convert_old_originator_to_new_originator(delivery_paid_orders)
            
            order_originators = sorted(list(dict.fromkeys([x.delivery_originator for x in delivery_paid_orders])))
            
            for originator in order_originators:
                if originator:
                    qty_delivery_brand_orders = len([x for x in delivery_paid_orders
                                                     if x.delivery_originator == originator])
                    value_delivery_brand_orders = sum([x.total for x in delivery_paid_orders
                                                       if x.delivery_originator == originator])
                    body += u"    {0:.<13}: [{1:>4}] R${2:>10}\n".format(originator[:13],
                                                                         qty_delivery_brand_orders,
                                                                         self._str_float(value_delivery_brand_orders))
        if manual_delivery_paid_orders:
            body += u"  {0:.<13}: [{1:>4}] R${2:>10}\n".format("Delivery Manual",
                                                               qty_manual_delivery_orders,
                                                               self._str_float(value_manual_delivery_orders))

        body += u"======================================\n"

        print_donation_or_tip = False
        if report_type != self.TypeXml and value_donation:
            body += u"Doacoes..........: [{0:>4}] R${1:>10}\n".format(qty_donation, self._str_float(value_donation))
            print_donation_or_tip = True

        if report_type != self.TypeXml and is_table_service:
            if operator_id == "0" or operator_id is None:
                body += u"Gorjetas.........: [{0:>4}] R${1:>10}\n".format(qty_tip, self._str_float(value_tip))
            else:
                body += u"Taxas de Servico.: [{0:>4}] R${1:>10}\n".format(qty_tip, self._str_float(value_tip))
            print_donation_or_tip = True

        if print_donation_or_tip:
            body += u"======================================\n"

        body += self._write_payments(payments_by_brand, tef_card_brands)

        if report_type != self.TypeXml:
            body += u"Cancelamentos....: [{0:>4}] R${1:>10}\n".format(qty_total_voided, self._str_float(value_total_voided))
            body += u"  Pedidos........: [{0:>4}] R${1:>10}\n".format(qty_orders_voided, self._str_float(value_orders_voided))
            body += u"  Cupons.........: [{0:>4}] R${1:>10}\n".format(qty_coupons_voided, self._str_float(value_coupons_voided))
            if voided_lines is not None:
                body += u"Linhas Canceladas: [{0:>4}] R${1:>10}\n".format(qty_lines_voided, self._str_float(value_lines_voided))
        body += u"======================================\n"

        return body

    def _convert_old_originator_to_new_originator(self, delivery_paid_orders):
        for order in delivery_paid_orders:
            if order.delivery_originator in self.delivery_originator_relation:
                order.delivery_originator = self.delivery_originator_relation[order.delivery_originator]
        
            order.delivery_originator = order.delivery_originator.capitalize()

    def _build_body_only_with_payments(self, payments_by_brand, tef_card_brands):
        body = u"Descricao          Qtd    Total\n"
        body += u"======================================\n"
        body += self._write_payments(payments_by_brand, tef_card_brands)
        return body

    @staticmethod
    def _str_float(float_num):
        return locale.format("%.2f", float_num, True)

    @staticmethod
    def _fill_orders_sector(tables_by_sector, orders):
        # type: (Dict, List[Order]) -> List[Order]
        for order in orders:
            if order.table_id in tables_by_sector:
                source_table_id = tables_by_sector[order.table_id]["source_table_id"]
                if source_table_id is None:
                    order.sector = tables_by_sector[order.table_id]["sector"]
                else:
                    order.sector = tables_by_sector[source_table_id]["sector"]
        return orders

    @staticmethod
    def _get_delivery_orders_values(delivery_paid_orders):
        delivery_orders_count = len([x for x in delivery_paid_orders])
        delivery_orders_value = sum([x.total for x in delivery_paid_orders])
        return delivery_orders_count, delivery_orders_value

    @staticmethod
    def _get_opened_orders_values(pos_id, opened_orders):
        qty_opened_orders = 0
        value_opened_orders = 0.0
        if opened_orders:
            model = sysactions.get_model(pos_id)
            pos_ot = sysactions.get_posot(model)
            qty_opened_orders = len(opened_orders)
            for order_id in opened_orders:
                order = eTree.XML(pos_ot.orderPicture(orderid=order_id)).find(".//Order")
                value_opened_orders += float(order.get("totalGross"))

        return qty_opened_orders, value_opened_orders

    @staticmethod
    def _get_voided_order_values(voided_lines, voided_orders):
        qty_lines_voided, value_lines_voided = CashReport._get_voided_lines(voided_lines)
        qty_total_voided = len(voided_orders)
        value_total_voided = 0.0
        qty_orders_voided = 0
        value_orders_voided = 0.0
        qty_coupons_voided = 0
        value_coupons_voided = 0.0
        for order in voided_orders:
            if order.void_reason_id == '5':
                qty_coupons_voided += 1
                value_coupons_voided += order.total
            else:
                qty_orders_voided += 1
                value_orders_voided += order.total
            value_total_voided += order.total
        return qty_coupons_voided, \
               qty_lines_voided, \
               qty_orders_voided, \
               qty_total_voided, \
               value_coupons_voided, \
               value_lines_voided, \
               value_orders_voided, \
               value_total_voided

    @staticmethod
    def _get_voided_lines(voided_lines):
        qty_lines_voided = int(sum(line.quantity for line in voided_lines) if voided_lines else 0)
        value_lines_voided = sum(line.price for line in voided_lines) if voided_lines else 0.0
        return qty_lines_voided, value_lines_voided

    @staticmethod
    def _get_initial_balance(is_table_service, transfers):
        initial_balance = 0.0
        if is_table_service:
            for transfer in transfers:
                if transfer.type == 1:
                    initial_balance += transfer.amount
        return initial_balance

    def _get_paid_order_values(self, paid_orders):
        qty_paid_orders = len(paid_orders)
        qty_discount = 0
        qty_donation = 0
        qty_tip = 0
        value_paid_orders = 0.0
        value_discount = 0.0
        value_donation = 0.0
        value_tip = 0.0
        for order in paid_orders:
            value_paid_orders += order.total
            qty_tip, value_tip = self._get_tip_values(order, qty_tip, value_tip)
            qty_donation, value_donation = self._get_donation_values(order, qty_donation, value_donation)
            qty_discount, value_discount = self._get_discount_values(order, qty_discount, value_discount)

        return qty_paid_orders, \
               qty_discount, \
               qty_donation, \
               qty_tip, \
               value_paid_orders, \
               value_discount, \
               value_donation, \
               value_tip

    @staticmethod
    def _get_discount_values(order, qty_discount, value_discount):
        if order.discount > 0:
            value_discount += order.discount
            qty_discount += 1
        return qty_discount, value_discount

    @staticmethod
    def _get_donation_values(order, qty_donation, value_donation):
        if order.donation > 0:
            value_donation += order.donation
            qty_donation += 1
        return qty_donation, value_donation

    @staticmethod
    def _get_tip_values(order, qty_tip, value_tip):
        if order.tip > 0:
            value_tip += order.tip
            qty_tip += 1
        return qty_tip, value_tip

    @staticmethod
    def _get_grouped_paid_orders_by_sector(paid_orders):
        grouped_paid_orders_by_sector = {}
        for order in paid_orders:
            if order.sector:
                if order.sector not in grouped_paid_orders_by_sector:
                    grouped_paid_orders_by_sector[order.sector] = {"value": order.total, "quantity": 1}
                else:
                    grouped_paid_orders_by_sector[order.sector]["value"] += order.total
                    grouped_paid_orders_by_sector[order.sector]["quantity"] += 1
        return grouped_paid_orders_by_sector

    def _build_table_info(self, average_info, paid_orders):
        """
        TM Mesa..........: [XXXX] R$ 00.000,00
        TM Cliente.......: [XXXX] R$ 00.000,00
        Giro Mesa   .....: hh:mm:ss

        ======================================
        :return: the report bytes encoded with UTF-8
        """

        value_paid_orders = 0.0
        for order in paid_orders:
            value_paid_orders += order.total

        seconds = (average_info.table_time_average_milliseconds / 1000) % 60
        seconds = int(seconds)
        minutes = (average_info.table_time_average_milliseconds / (1000 * 60)) % 60
        minutes = int(minutes)
        hours = (average_info.table_time_average_milliseconds / (1000 * 60 * 60)) % 24

        if average_info.total_tables != 0:
            tm = value_paid_orders / average_info.total_tables
        else:
            tm = 0

        if average_info.total_customers != 0:
            tc = value_paid_orders / average_info.total_customers
        else:
            tc = 0
        table_info = ""
        table_info += u"TM Mesa..........: [{0:>4}] R${1:>10}\n".format(average_info.total_tables, self._str_float(tm))
        table_info += u"TM Cliente.......: [{0:>4}] R${1:>10}\n".format(average_info.total_customers, self._str_float(tc))
        table_info += u"Giro Mesa........:            {} \n".format("%02d:%02d:%02d" % (hours, minutes, seconds))
        table_info += u"======================================\n"

        return table_info

    def _write_payments(self, payments_by_brand, tef_card_brands):
        # type: (List[Tuple[unicode, int, float, int]], dict) -> unicode
        payments_text = u"Pagamentos.......: [{payment_qty:>4}] R${payment_value:>10}\n"
        payment_qty = 0
        payment_value = 0

        for card_brand in payments_by_brand:
            tender_id = [payments_by_brand[card_brand][x]['id'] for x in payments_by_brand[card_brand]][0]
            brand_quantity_sum = sum([payments_by_brand[card_brand][x]['quantity'] for x in payments_by_brand[card_brand]])
            brand_value_sum = sum([payments_by_brand[card_brand][x]['value'] for x in payments_by_brand[card_brand]])
            payment_qty += brand_quantity_sum
            payment_value += brand_value_sum

            if self.print_card_brands:
                payments_text += u" {0:.<16}: [{1:>4}] R${2:>10}\n".format(card_brand[:16],
                                                                           brand_quantity_sum,
                                                                           self._str_float(brand_value_sum))

                if tender_id in [TenderType.credit, TenderType.debit]:
                    for tef_brand, brand_tender_id in tef_card_brands:
                        if brand_tender_id == tender_id:
                            payments_text += u"  {0:.<15}: [{1:>4}] R${2:>10}\n".format(tef_brand[:15],
                                                                                        tef_card_brands[(tef_brand, brand_tender_id)]["quantity"],
                                                                                        self._str_float(tef_card_brands[(tef_brand, brand_tender_id)]["value"]))

                if len(payments_by_brand[card_brand]) == 1 and card_brand in payments_by_brand[card_brand]:
                    continue

                for sub_card_brand in payments_by_brand[card_brand]:
                    qty = payments_by_brand[card_brand][sub_card_brand]['quantity']
                    value = payments_by_brand[card_brand][sub_card_brand]['value']
                    payments_text += u"  {0:.<15}: [{1:>4}] R${2:>10}\n".format(sub_card_brand[:15],
                                                                                qty,
                                                                                self._str_float(value))

        payments_text += u"======================================\n"

        return payments_text.format(payment_qty=payment_qty, payment_value=self._str_float(payment_value))

    def _generate_cash_report_json(self, pos_id, report_pos, initial_date, end_date, operator_id, business_period, codigo_centro, close_time):
        # type: (int, Optional[unicode], datetime, datetime, unicode, unicode, unicode, datetime) -> str

        paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
        voided_orders = self.order_repository.get_voided_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
        transfers = self.account_repository.get_transfers_by_business_period(initial_date, end_date, operator_id, report_pos)
        card_brands = self.fiscal_repository.get_card_brands(paid_orders)
        operators_qty = self.pos_ctrl_repository.get_operators_qty(pos_id, business_period)

        json_report = self._build_json(pos_id, paid_orders, voided_orders, transfers, operators_qty, business_period, codigo_centro, close_time, card_brands)

        return json_report.encode("utf-8")

    def _build_json(self, pos_id, paid_orders, voided_orders, transfers, operators_qty, business_period, codigo_centro, close_time, card_brands):
        # type: (int, List[Order], List[Order], List[Transfer], int, unicode, unicode, datetime, List[Tuple[unicode, int, float, int]]) -> unicode
        qty_paid_orders = len(paid_orders)
        value_paid_orders = 0.0
        total_tender_by_type_dict = {}  # type: Dict[int, TotalTender]
        total_tender = ''
        qty_donation = 0
        value_donation = 0.0
        for order in paid_orders:
            value_paid_orders += order.total
            qty_donation += 1 if order.donation > 0 else 0
            value_donation += order.donation
            self._calc_tenders_by_type(order, total_tender_by_type_dict)

        total_tender_by_type_list = []  # type: List[TotalTender]
        for tender_type_id in total_tender_by_type_dict:
            tender_type = total_tender_by_type_dict[tender_type_id]
            tender_type.name = total_tender.tender_name

            total_tender_by_type_list.append(tender_type)

        sorted(total_tender_by_type_list, key=lambda x: x.tender_type)

        qty_voided_orders = len(voided_orders)
        value_voided_orders = 0.0
        for order in voided_orders:
            value_voided_orders += order.total

        initial_balance = 0.0
        value_sangria = 0.0
        qty_sangria = 0
        value_suprimento = 0.0
        qty_suprimento = 0
        for transfer in transfers:
            if transfer.type == 1:
                initial_balance += transfer.amount
            elif transfer.type == 2:
                value_sangria += transfer.amount
                qty_sangria += 1
            elif transfer.type == 3:
                value_suprimento += transfer.amount
                qty_suprimento += 1

        tender_types = {}

        for total_tender in total_tender_by_type_list:
            tender_types[total_tender.tender_name] = {'quantity': total_tender.quantity,
                                                      'amount': round(total_tender.value, 2),
                                                      'details': None}

            if total_tender.tender_type != 0:
                tender_types[total_tender.tender_name]['details'] = {}
                tender_total_qty = 0
                tender_total_value = 0

                for brand in card_brands:
                    if total_tender.tender_type == brand[1]:
                        tender_total_qty += brand[3]
                        tender_total_value += brand[2]
                        tender_types[total_tender.tender_name]['details'][brand[0]] = {'quantity': brand[3],
                                                                                       'amount': round(brand[2], 2)}
                tender_types[total_tender.tender_name]['quantity'] = tender_total_qty
                tender_types[total_tender.tender_name]['amount'] = round(tender_total_value, 2)

        response = {
            'branchNumber': str(self.store_id),
            'restaurantId': str(codigo_centro),
            'closeTime': close_time,
            'pdvNumber': pos_id,
            'businessPeriod': str(business_period),
            'initialBalance': round(initial_balance, 2),
            'operators': operators_qty,
            'ordersQuantity': qty_paid_orders + qty_voided_orders,
            'quantityPaidOrders': qty_paid_orders,
            'valuePaidOrders': round(value_paid_orders, 2),
            'quantityVoidedOrders': qty_voided_orders,
            'valueVoidedOrders': round(value_voided_orders, 2),
            'quantitySkim': qty_sangria,
            'valueSkim': round(value_sangria, 2),
            'quantityCashIn': qty_suprimento,
            'valueCashIn': round(value_suprimento, 2),
            'quantityDonation': qty_donation,
            'valueDonation': round(value_donation, 2),
            'tenderTypes': tender_types
        }

        return json.dumps(response)

    def generate_hourly_sale(self, report_pos, initial_date, end_date, operator):
        return self.order_repository.get_hourly_sale(report_pos, initial_date, end_date, operator)

    def generate_paid_order_cash_report_by_date(self, initial_date, end_date):
        return self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, None, None)

    def generate_paid_orders_value_report(self, initial_date, end_date):
        # type: (datetime, datetime) -> unicode
        paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, None, None)

        value_paid_orders = 0
        for order in paid_orders:
            value_paid_orders += order.total

        return unicode(value_paid_orders)
