import json
import locale
from datetime import datetime

from sysactions import get_storewide_config
from typing import Dict, List, Optional, Tuple

from repository import OrderRepository, AccountRepository, TenderRepository, FiscalRepository, PosCtrlRepository
from .model import Order, TotalTender, TenderType, Transfer


class CashReport(object):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"
    TypeXml = "Xml"

    def __init__(self, order_repository, account_repository, tender_repository, fiscal_repository, pos_ctrl_repository, store_id):
        # type: (OrderRepository, AccountRepository, TenderRepository, FiscalRepository, PosCtrlRepository, unicode) -> None
        self.order_repository = order_repository
        self.account_repository = account_repository
        self.tender_repository = tender_repository
        self.fiscal_repository = fiscal_repository
        self.pos_ctrl_repository = pos_ctrl_repository
        self.store_id = store_id

        self.tender_names_dict = {}  # type: Dict[int, unicode]
        for tender_tuple in self.tender_repository.get_tender_names():
            self.tender_names_dict[tender_tuple[0]] = tender_tuple[1]

    def generate_cash_report_by_real_date(self, pos_id, report_pos, initial_date, end_date, operator_id):
        # type: (int, Optional[unicode], datetime, datetime, unicode) -> str
        return self._generate_cash_report(self.TypeRealDate, pos_id, report_pos, initial_date, end_date, operator_id, None)

    def generate_cash_report_by_business_period(self, pos_id, report_pos, initial_date, end_date, operator_id, business_period=None, codigo_centro=None, close_time=None):
        # type: (int, Optional[unicode], datetime, datetime, unicode, Optional[unicode], Optional[unicode], Optional[datetime]) -> str

        if business_period is None:
            return self._generate_cash_report(self.TypeBusinessPeriod, pos_id, report_pos, initial_date, end_date, operator_id, None)
        else:
            return self._generate_cash_report_json(pos_id, report_pos, initial_date, end_date, operator_id, business_period, codigo_centro, close_time)

    def generate_cash_report_by_session_id(self, pos_id, session_id):
        # type: (int, unicode) -> str
        return self._generate_cash_report(self.TypeSessionId, pos_id, None, None, None, None, session_id)

    def generate_cash_report_by_xml(self, pos_id, initial_date, end_date):
        # type: (int, datetime, datetime) -> str
        return self._generate_cash_report(self.TypeXml, pos_id, None, initial_date, end_date, None, None)

    def _generate_cash_report(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id):
        # type: (unicode, int, Optional[unicode], Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> str
        if report_type == self.TypeRealDate:
            paid_orders = self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, operator_id, report_pos)
            voided_orders = self.order_repository.get_voided_orders_by_real_date(initial_date, end_date, operator_id, report_pos)
            transfers = self.account_repository.get_transfers_by_real_date(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeBusinessPeriod:
            paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
            voided_orders = self.order_repository.get_voided_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
            transfers = self.account_repository.get_transfers_by_business_period(initial_date, end_date, operator_id, report_pos)

        elif report_type == self.TypeSessionId:
            paid_orders = self.order_repository.get_paid_orders_by_session_id(session_id)
            voided_orders = self.order_repository.get_voided_orders_by_session_id(session_id)
            transfers = self.account_repository.get_transfers_by_session_id(session_id)
            start_index = session_id.find("user=")
            end_index = session_id.find(",", start_index)
            operator_id = session_id[start_index + 5:end_index]
            start_index = session_id.find("period=")
            initial_date = end_date = datetime.strptime(session_id[start_index + 7:], "%Y%m%d")

        else:
            paid_orders = self.order_repository.get_paid_orders_by_xml(initial_date, end_date)
            voided_orders = self.order_repository.get_voided_orders_by_xml(initial_date, end_date)
            transfers = self.account_repository.get_transfers_by_real_date(initial_date, end_date, None, report_pos)
            operator_id = None

        card_brands = None
        try:
            if get_storewide_config("Store.PrintCardBrands", defval="False").lower() == "true":
                card_brands = self.fiscal_repository.get_card_brands(paid_orders)
        except Exception as _:
            pass

        count_pos_error = filter(lambda x:x == "error", paid_orders)
        count_pos_error = len(count_pos_error)

        paid_orders = filter(lambda x: x != "error", paid_orders)
        voided_orders = filter(lambda x: x != "error", voided_orders)

        header = self._build_header(report_type, pos_id, report_pos, initial_date, end_date, operator_id, count_pos_error)
        body = self._build_body(paid_orders, voided_orders, transfers, report_type, card_brands)

        report = header + body
        report_bytes = report.encode("utf-8")

        return report_bytes

    def _generate_cash_report_json(self, pos_id, report_pos, initial_date, end_date, operator_id, business_period, codigo_centro, close_time):
        # type: (int, Optional[unicode], datetime, datetime, unicode, unicode, unicode, datetime) -> str

        paid_orders = self.order_repository.get_paid_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
        voided_orders = self.order_repository.get_voided_orders_by_business_period(initial_date, end_date, operator_id, report_pos)
        transfers = self.account_repository.get_transfers_by_business_period(initial_date, end_date, operator_id, report_pos)
        card_brands = self.fiscal_repository.get_card_brands(paid_orders)
        operators_qty = self.pos_ctrl_repository.get_operators_qty(pos_id, business_period)

        json_report = self._build_json(pos_id, paid_orders, voided_orders, transfers, operators_qty, business_period, codigo_centro, close_time, card_brands)

        return json_report.encode("utf-8")

    def generate_paid_order_cash_report_by_date(self, initial_date, end_date):
        return self.order_repository.get_paid_orders_by_real_date(initial_date, end_date, None, None)

    def _build_header(self, report_type, pos_id, report_pos, initial_date, end_date, operator_id, count_pos_error=0):
        # type: (unicode, int, Optional[unicode], datetime, datetime, unicode, int) -> unicode
        """
        ======================================
              Relatorio de Vendas(Loja)
          Loja..........: 99999
          Data/hora.....: 01/08/2017 09:59:26
          Dia Util......: 31/07/2017
          ID Operador ..: Todos (Reg # 03)
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
        elif report_type == self.TypeXml:
            report_type_text = "Arquivo Xml"
        else:
            report_type_text = "Surpresa"
            pos_list = pos_id

        header =  u"======================================\n"
        header += u"   Relatorio de Vendas - {0}  \n".format(report_type_text)
        header += u" Loja.........: " + self.store_id.zfill(5) + "\n"
        header += u" Data/hora....: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "\n"
        header += u" {0:.<13}: {1} - {2}\n".format(report_type_text, initial_date.strftime("%d/%m/%y"), end_date.strftime("%d/%m/%y"))
        header += u" ID Operador..: " + u"{0} (Reg # {1})\n".format(operator, str(pos_id).zfill(2))
        header += u" POS incluido.: " + u"{0}\n".format(pos_list)
        if count_pos_error > 0:
            header += u" POS excluidos: " + u"{0}\n".format(count_pos_error)

        header += u"======================================\n"

        return header

    def _build_body(self, paid_orders, voided_orders, transfers, report_type, card_brands=None):
        # type: (List[Order], List[Order], List[Transfer], unicode, Optional[List[Tuple[unicode, int, float, int]]]) -> unicode
        """
        Descricao           Qtd   Total
        Balanco Inicial..:        R$      0.00
        Operadores.......: [XXXX]
        Vendas...........: [XXXX] R$ 00.000,00
        Cancelamentos....: [XXXX] R$ 00.000,00
          Pedidos........: [XXXX] R$ 00.000,00
          Cupons.........: [XXXX] R$ 00.000,00
        Venda Liquida....: [XXXX] R$ 00.000,00
        Total Recebido...:
          DINHEIRO.......: [XXXX] R$ 00.000,00
          CARTAO CREDITO.: [XXXX] R$ 00.000,00
          CARTAO DEBITO..: [XXXX] R$ 00.000,00
          SpoonRocket....: [XXXX] R$ 00.000,00
        Sangria..........: [XXXX] R$ 00.000,00
        Suprimentos......: [XXXX] R$ 00.000,00
        Doacoes..........: [XXXX] R$ 00.000,00
        Valor na Gaveta..:        R$ 00.000,00
        ======================================
        :param paid_orders: the list of paid orders
        :param voided_orders: the list of voided orders
        :param transfers: the list of all transfers
        :return: the report bytes encoded with UTF-8
        """

        qty_paid_orders = len(paid_orders)
        value_paid_orders = 0.0
        value_doacoes = 0.0
        qty_doacoes = 0
        value_discount = 0.0
        qty_discount = 0
        total_tender_by_type_dict = {}  # type: Dict[int, TotalTender]
        total_tender = ''
        for order in paid_orders:
            value_paid_orders += order.total
            if order.donation > 0:
                value_doacoes += order.donation
                qty_doacoes += 1
            if order.discount > 0:
                value_discount += order.discount
                qty_discount += 1
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

        qty_total_voided = len(voided_orders)
        value_total_voided = 0.0
        qty_orders_voided = 0
        value_orders_voided = 0.0
        qty_coupons_voided = 0
        value_coupons_voided = 0.0

        for order in voided_orders:
            if order.void_reason_id == '5':
                # voided by 'cancel last order' button
                qty_coupons_voided += 1
                value_coupons_voided += order.total
            else:
                qty_orders_voided += 1
                value_orders_voided += order.total
            value_total_voided += order.total

        initial_balance = 0.0
        value_sangria = 0.0
        qty_sangria = 0
        value_suprimento = 0.0
        qty_suprimento = 0
        final_balance = 0.0  # Final balance should not be shown
        for transfer in transfers:
            if transfer.type == 1:
                initial_balance += transfer.amount
            elif transfer.type == 2:
                value_sangria += transfer.amount
                qty_sangria += 1
            elif transfer.type == 3:
                value_suprimento += transfer.amount
                qty_suprimento += 1
            elif transfer.type == 5:
                final_balance += transfer.amount

        money_sales = 0.0
        if TenderType.Money in total_tender_by_type_dict:
            money_sales = total_tender_by_type_dict[TenderType.Money].value

        drawer_value = initial_balance + value_suprimento + value_doacoes - value_sangria + money_sales - final_balance

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        body = u"Descricao           Qtd   Total\n"
        body += u"Balanco Inicial..:        R${0:>10}\n".format(locale.format("%.2f", initial_balance, True))
        if report_type != self.TypeXml:
            body += u"Cancelamentos....: [{0:>4}] R${1:>10}\n".format(qty_total_voided, locale.format("%.2f", value_total_voided, True))
            body += u"  Pedidos........: [{0:>4}] R${1:>10}\n".format(qty_orders_voided, locale.format("%.2f", value_orders_voided, True))
            body += u"  Cupons.........: [{0:>4}] R${1:>10}\n".format(qty_coupons_voided, locale.format("%.2f", value_coupons_voided, True))
        body += u"Vendas...........: [{0:>4}] R${1:>10}\n".format(qty_paid_orders + qty_total_voided, locale.format("%.2f", value_paid_orders + value_total_voided, True))
        body += u"Venda Liquida....: [{0:>4}] R${1:>10}\n".format(qty_paid_orders, locale.format("%.2f", value_paid_orders, True))
        body += self._get_payments_text(card_brands, total_tender_by_type_list)
        body += u"Sangria..........: [{0:>4}] R${1:>10}\n".format(qty_sangria, locale.format("%.2f", value_sangria, True))
        body += u"Suprimentos......: [{0:>4}] R${1:>10}\n".format(qty_suprimento, locale.format("%.2f", value_suprimento, True))
        if report_type != self.TypeXml:
            body += u"Doacoes..........: [{0:>4}] R${1:>10}\n".format(qty_doacoes, locale.format("%.2f", value_doacoes, True))
        body += u"Descontos........: [{0:>4}] R${1:>10}\n".format(qty_discount, locale.format("%.2f", value_discount, True))
        body += u"Valor na Gaveta..:        R${0:>10}\n".format(locale.format("%.2f", drawer_value, True))
        body += u"======================================\n"

        return body

    @staticmethod
    def _get_payments_text(card_brands, total_tender_by_type_list):
        # type: (List[Tuple[unicode, int, float, int]], List[TotalTender]) -> unicode

        payments_text = u"  Pagamentos.....: [{payment_qty:>4}] R${payment_value:>10}\n"
        payment_qty = 0
        payment_value = 0
        if card_brands is None:
            for total_tender in total_tender_by_type_list:
                payment_qty += total_tender.quantity
                payment_value += total_tender.value
                payments_text += u"  {0:.<15}: [{1:>4}] R${2:>10}\n".format(total_tender.tender_name, total_tender.quantity, locale.format("%.2f", total_tender.value, True))
        else:
            for total_tender in total_tender_by_type_list:
                payment_qty += total_tender.quantity
                payment_value += total_tender.value
                if total_tender.tender_type == 0:
                    payments_text += u" {0:.<16}: [{1:>4}] R${2:>10}\n".format(total_tender.tender_name, total_tender.quantity, locale.format("%.2f", total_tender.value, True))
                else:
                    payments_text += u" {0:.<16}:\n".format(total_tender.tender_name)
                    for brand in card_brands:
                        if total_tender.tender_type == brand[1]:
                            payments_text += u"  {0:.<15}: [{1:>4}] R${2:>10}\n".format(brand[0][:15], brand[3], locale.format("%.2f", brand[2], True))

        return payments_text.format(payment_qty=payment_qty, payment_value=locale.format("%.2f", payment_value, True))

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
