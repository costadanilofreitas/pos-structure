from datetime import datetime
from repository import OrderRepository, ProductRepository
from .model import OrderItem
from typing import List, Optional

# COMMENT HERE
import sys
import os

debugPath = '../python/pycharm-debug.egg'
if os.path.exists(debugPath):
    try:
        sys.path.index(debugPath)
    except:
        sys.path.append(debugPath)
    import pydevd

# Use the line below in the function you want to debug
# pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True, suspend=False)
# UNTIL HERE


class PMixReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"

    def __init__(self, order_repository, product_repository, store_id):
        # type: (OrderRepository, ProductRepository, unicode) -> None
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.store_id = store_id

    def generate_pmix_report_by_real_date(self, pos_id, initial_date, end_date):
        # type: (int, Optional[datetime], Optional[datetime]) -> str
        return self._generate_pmix_report(self.TypeRealDate, pos_id, initial_date, end_date)

    def generate_pmix_report_by_business_period(self, pos_id, initial_date, end_date):
        # type: (int, Optional[datetime], Optional[datetime]) -> str
        return self._generate_pmix_report(self.TypeBusinessPeriod, pos_id, initial_date, end_date)

    def _generate_pmix_report(self, report_type, pos_id, initial_date, end_date):
        # type: (unicode, int, Optional[datetime], Optional[datetime]) -> str

        if report_type == self.TypeRealDate:
            paid_orders = self.order_repository.get_paid_orders_by_real_date(initial_date, end_date)
        else:
            paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date)
        order_items = self.order_repository.get_orders_items(paid_orders)

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

        header = self._build_header(pos_id, initial_date, end_date, report_type, count_pos_error)
        body = self._build_body(order_items)

        report = header + body
        report_bytes = report.encode("utf-8")

        return report_bytes

    def _build_header(self, pos_id, initial_date, end_date, report_type, count_pos_error=0):
        # type: (int, datetime, datetime) -> unicode
        """
        ======================================
                  Mix de Produtos(Loja)
          Loja..........: 99999
          Data/hora.....: 01/08/2017 09:59:26
          Dia Util......: 31/07/2017
          ID Operador ..: Todos (Reg # 03)
          POS incluido..: Todos
        ======================================"""
        operator = "Todos"
        pos_list = "Todos" if len(self.order_repository.pos_list) > 1 else self.order_repository.pos_list[0]

        header =  u"======================================\n"
        header += u"     Mix de Produtos ({0})     \n".format("Data Fiscal" if report_type == self.TypeRealDate else "Data Negocio")
        header += u" Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        header += u" Dia Util.....: {0} - {1}\n".format(initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" ID Operador..: " + u"{0} (Reg # {1})\n".format(operator, str(pos_id).zfill(2))
        header += u" POS incluido.: " + u"{0}\n".format(pos_list)
        if count_pos_error > 0:
            header += u" POS excluidos: " + u"{0}\n".format(count_pos_error)
        header += u"======================================\n"

        return header

    def _build_body(self, order_items):
        """
        Codigo   Descricao                 Qtd
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        0000000  XXXXXXXXXX                000
        ======================================
        :param order_items: the list of items
        :return: the report bytes encoded with UTF-8
        """
        # type: (List[OrderItem]) -> unicode

        body = u"Codigo   Descricao                 Qtd\n"
        for order_item in order_items:
            body += u"{0:0>7}  {1:<23} {2:>5}\n".format(order_item.pcode, self._unicode_2_ascii(order_item.name)[23:], order_item.quantity)
        body += u"======================================\n"

        return body

    def _unicode_2_ascii(self, data):
        import unicodedata
        # punctuation = {0x2018: 0x27, 0x2019: 0x27, 0x201C: 0x22, 0x201D: 0x22}
        # data = data.translate(punctuation)
        data = data.decode('UTF-8')
        data = unicode(data)
        data = unicodedata.normalize('NFKD', data)
        data = data.encode('ascii', 'ignore')
        return data
