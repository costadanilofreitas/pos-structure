# encoding: utf-8

import locale
import xml.etree.cElementTree as eTree
from datetime import datetime
from unicodedata import normalize

import sysactions
from typing import List, Optional

from repository import OrderRepository, ProductRepository
from .model import OrderItem


class PMixReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"
    TypeXml = "Xml"

    def __init__(self, order_repository, product_repository, store_id, operator_id):
        # type: (OrderRepository, ProductRepository, str, str) -> None
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.store_id = store_id
        self.operator_id = operator_id

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

    def generate_pmix_report_by_real_date(self, pos_id, initial_date, end_date, report_model, operatorid="operatorid"):
        # type: (int, Optional[datetime], Optional[datetime], str, Optional[str]) -> str
        return self._generate_pmix_report(self.TypeRealDate, pos_id, initial_date, end_date, report_model, operatorid)

    def generate_pmix_report_by_business_period(self, pos_id, initial_date, end_date, report_model, operatorid="operatorid"):
        # type: (int, Optional[datetime], Optional[datetime], str, Optional[str]) -> str
        return self._generate_pmix_report(self.TypeBusinessPeriod, pos_id, initial_date, end_date, report_model, operatorid)

    def _generate_pmix_report(self, report_type, pos_id, initial_date, end_date, report_model, operator_id=""):
        # type: (unicode, int, datetime, datetime, str, Optional[str]) -> str

        if report_type == self.TypeRealDate:
            paid_orders = self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, operator_id)
        else:
            paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, operator_id)

        order_items = self.order_repository.get_orders_items(paid_orders)
        order_items = self.filter_order_items(order_items, report_model)

        count_pos_error = filter(lambda x:x == "error", order_items)
        count_pos_error = len(count_pos_error)

        order_items = filter(lambda x: x != "error", order_items)

        order_items = self.product_repository.get_order_items_names(order_items)

        grouped_order_items = {}
        for item in order_items:
            if item.pcode not in grouped_order_items.keys():
                grouped_order_items[item.pcode] = item
            else:
                grouped_order_items[item.pcode].quantity += item.quantity

        order_items = grouped_order_items.values()
        order_items = sorted(order_items, key=lambda order_item: order_item.pcode)

        header = self._build_header(pos_id, initial_date, end_date, report_type, operator_id, report_model, count_pos_error)
        body = self._build_body(order_items)

        report = header + body
        report_bytes = report.encode("utf-8")

        return report_bytes

    @staticmethod
    def filter_order_items(order_items, report_model):
        if report_model == "PRICED":
            return [x for x in order_items if x.unit_price != 0]
        elif report_model == "UNPRICED":
            return [x for x in order_items if x.unit_price == 0]
        else:
            return order_items

    def generate_pmix_order_items(self, initial_date, end_date):
        # type: (Optional[datetime], Optional[datetime]) -> List[OrderItem]
        _, order_items = self._get_order_items(initial_date, end_date, self.TypeBusinessPeriod)
        return order_items

    def _get_order_items(self, initial_date, end_date, report_type):
        if report_type == self.TypeRealDate:
            paid_orders = self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, self.operator_id)
        else:
            paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, self.operator_id)
        order_items = self.order_repository.get_orders_items(paid_orders)
        count_pos_error = filter(lambda x: x == "error", order_items)
        count_pos_error = len(count_pos_error)
        order_items = filter(lambda x: x != "error", order_items)
        order_items = self.product_repository.get_order_items_names(order_items)
        grouped_order_items = {}
        for item in order_items:
            if item.pcode not in grouped_order_items.keys():
                grouped_order_items[item.pcode] = item
            else:
                grouped_order_items[item.pcode].quantity += item.quantity
        order_items = grouped_order_items.values()
        order_items = sorted(order_items, key=lambda order_item: order_item.pcode)
        return count_pos_error, order_items

    def _build_header(self, pos_id, initial_date, end_date, report_type, operator_id, report_model, count_pos_error=0):
        # type: (int, datetime, datetime, str, str, str, Optional[int]) -> unicode
        if operator_id not in ["0", "", "None"]:
            operator_name = eTree.XML(sysactions.get_user_information(operator_id)).find(".//user").get("LongName")[:20]
        else:
            operator_name = "Todos"
        pos_list = "Todos" if len(self.order_repository.pos_list) > 1 else self.order_repository.pos_list[0]

        model = sysactions.get_model(pos_id)

        header = u"======================================\n"
        header += u"     Mix de Produtos ({0})     \n".format("Data Fiscal" if report_type == self.TypeRealDate else "Data Negocio")
        header += u" Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        if report_type != self.TypeSessionId:
            header += u" {0:.<13}: {1} - {2}\n".format("Periodo", initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" Operador.....: " + u"{0}\n".format(operator_name[:20])
        temp_pos_list = u" POS incluidos: " + u"{0}".format(pos_list)
        header += temp_pos_list[:36]
        if len(temp_pos_list) > 36:
            header += (u"\n                %s" % temp_pos_list[36:56])
        if len(temp_pos_list) > 62:
            header += (u"\n                %s" % temp_pos_list[56:76])
        header += u"\n"
        header += u" Modelo.......: {}\n".format(_remove_accents(sysactions.translate_message(model, report_model)))
        if count_pos_error > 0:
            header += u" POS excluidos: " + u"{0}\n".format(count_pos_error)
        header += u"======================================\n"

        return header

    @staticmethod
    def _build_body(order_items):
        # type: (List[OrderItem]) -> unicode
        body = u"Codigo   Descricao                 Qtd\n"
        body += u"--------------------------------------\n"
        for order_item in sorted(order_items, key=lambda x: x.name):
            body += u"{0:0>7}  {1:<21} {2:>7}\n".format(order_item.pcode,
                                                        _remove_accents(order_item.name)[:21],
                                                        _str_float(order_item.quantity))
        body += u"======================================\n"

        return body


def _remove_accents(text):
    return normalize('NFKD', unicode(text.decode('utf8'))).encode('ascii', 'ignore')


def _str_float(float_num):
    return locale.format("%.2f", float_num, True).replace(",", ".")
