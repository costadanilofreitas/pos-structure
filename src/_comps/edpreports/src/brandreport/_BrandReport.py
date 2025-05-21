import locale
from datetime import datetime

from pos_model import TenderType
from typing import Dict, List, Optional, Tuple

from repository import OrderRepository, FiscalRepository, TenderRepository
from .model import Order, TotalTender


class BrandReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, order_repository, fiscal_repository, tender_repository, store_id):
        # type: (OrderRepository, FiscalRepository, TenderRepository, unicode) -> None
        self.order_repository = order_repository
        self.fiscal_repository = fiscal_repository
        self.tender_repository = tender_repository
        self.store_id = store_id

        self.tender_names_dict = {}  # type: Dict[int, unicode]
        for tender_tuple in self.tender_repository.get_tender_names():
            self.tender_names_dict[tender_tuple[0]] = tender_tuple[1]

    def generate_brand_report_by_real_date(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, Optional[unicode]) -> str
        return self._generate_brand_report(self.TypeRealDate, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_brand_report_by_business_period(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, unicode) -> str
        return self._generate_brand_report(self.TypeBusinessPeriod, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_brand_report_by_session_id(self, pos_id, session_id):
        # type: (int, unicode) -> str
        return self._generate_brand_report(self.TypeSessionId, pos_id, None, None, None, None, session_id)

    def _generate_brand_report(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id):
        # type: (unicode, int, Optional[unicode], Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> str

        if report_type == self.TypeRealDate:
            paid_orders = self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeBusinessPeriod:
            paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeSessionId:
            paid_orders = self.order_repository.get_paid_orders_by_session_id(session_id)
            start_index = session_id.find("user=")
            end_index = session_id.find(",", start_index)
            operator_id = session_id[start_index + 5:end_index]
            start_index = session_id.find("period=")
            initial_date = end_date = datetime.strptime(session_id[start_index + 7:], "%Y%m%d")

        else:
            raise NotImplementedError()

        count_pos_error = filter(lambda x:x == "error", paid_orders)
        count_pos_error = len(count_pos_error)

        paid_orders = filter(lambda x: x != "error", paid_orders)

        card_brands = self.fiscal_repository.get_card_brands(paid_orders)

        header = self._build_header(report_type, pos_id, report_pos, initial_date, end_date, operator_id, count_pos_error)
        body = self._build_body(paid_orders, card_brands)

        report = header + body
        report_bytes = report.encode("utf-8")

        return report_bytes

    def _build_header(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, count_pos_error=0):
        # type: (unicode, int, Optional[unicode], datetime, datetime, unicode) -> unicode
        """
        ======================================
          Relatorio de Pagamentos por Bandeira
                        (Loja)
          Loja..........: 99999
          Data/hora.....: 01/08/2017 09:59:26
          Dia Util......: 31/07/2017
          ID Operador ..: Todos (POS # 03)
          POS incluido..: Todos
        ======================================"""
        operator = "Todos"
        if operator_id is not None:
            operator = operator_id

        pos_list = "Todos" if report_pos is None else report_pos.zfill(2)
        if report_type == self.TypeRealDate:
            report_type_text = "Data Fiscal"
        elif report_type == self.TypeBusinessPeriod:
            report_type_text = "Dia Negocio"
        else:
            report_type_text = "Surpresa"
            pos_list = pos_id

        header =  u"======================================\n"
        header += u" Relatorio de Pagamentos por Bandeira  \n"
        header += u"({})".format(report_type_text).center(38) + "\n"
        header += u" Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        header += u" {0:.<13}: {1} - {2}\n".format(report_type_text, initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" ID Operador..: " + u"{0} (POS # {1})\n".format(operator, str(pos_id).zfill(2))
        header += u" POS incluido.: " + u"{0}\n".format(pos_list)
        if count_pos_error > 0:
            header += u" POS excluidos: " + u"{0}\n".format(count_pos_error)
        header += u"======================================\n"

        return header

    def _build_body(self, paid_orders, card_brands):
        # type: (List[Order], List[Tuple[unicode, int, float, int]]) -> unicode

        """
        Descricao          Qtd    Total
          DINHEIRO.......: [XXXX] R$ 00.000,00
          CARTAO CREDITO.: [XXXX] R$ 00.000,00
          CARTAO DEBITO..: [XXXX] R$ 00.000,00
          SpoonRocket....: [XXXX] R$ 00.000,00
        ======================================
        :param paid_orders: the list of paid orders
        :param voided_orders: the list of voided orders
        :param transfers: the list of all transfers
        :return: the report bytes encoded with UTF-8
        """

        total_tender = ""
        value_paid_orders = 0.0
        total_tender_by_type_dict = {}  # type: Dict[int, TotalTender]
        for order in paid_orders:
            value_paid_orders += order.total
            for tender in order.tenders:
                if tender.type in total_tender_by_type_dict:
                    total_tender = total_tender_by_type_dict[tender.type]
                else:
                    total_tender = TotalTender()
                    total_tender.tender_type = tender.type
                    total_tender.quantity = 0
                    if total_tender.tender_type in self.tender_names_dict:
                        total_tender.tender_name = self.tender_names_dict[total_tender.tender_type]
                    else:
                        total_tender.tender_name = "OUTROS"
                    total_tender_by_type_dict[tender.type] = total_tender

                total_tender.quantity += 1
                total_tender.value += tender.value

        total_tender_by_type_list = []  # type: List[TotalTender]
        for tender_type_id in total_tender_by_type_dict.keys():
            tender_type = total_tender_by_type_dict[tender_type_id]
            tender_type.name = total_tender.tender_name

            total_tender_by_type_list.append(tender_type)

        sorted(total_tender_by_type_list, key=lambda x: x.tender_type)

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except Exception as _:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        body = u"Descricao         Qtd    Total\n"
        if card_brands is None:
            for total_tender in total_tender_by_type_list:
                body += u"{0:.<15}: [{1:>4}] R${2:>10}\n".format(total_tender.tender_name,
                                                                   total_tender.quantity,
                                                                   locale.format("%.2f", total_tender.value, True))
        else:
            for total_tender in total_tender_by_type_list:
                if total_tender.tender_type not in (TenderType.credit, TenderType.debit, TenderType.external_card):
                    body += u"{0:.<16}: [{1:>4}] R${2:>10}\n".format(total_tender.tender_name,
                                                                      total_tender.quantity,
                                                                      locale.format("%.2f", total_tender.value, True))
                else:
                    body += u"{0:.<16}:\n".format(total_tender.tender_name)
                    for brand in card_brands:
                        if total_tender.tender_type == brand[1]:
                            body += u"  {0:.<15}: [{1:>4}] R${2:>10}\n".format(brand[0][:15],
                                                                               brand[3],
                                                                               locale.format("%.2f", brand[2], True))
        body += u"======================================\n"

        return body
