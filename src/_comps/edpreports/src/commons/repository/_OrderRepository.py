# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta
from xml.etree import cElementTree as eTree

import iso8601
from helper import BaseRepository, ReportType
from msgbus import MBEasyContext  # noqa
from persistence import Connection  # noqa
from systools import sys_log_exception
from typing import List, Dict, Optional  # noqa

from reports_app.cashreport.dto import Order, OrderTender


class OrderRepository(BaseRepository):
    def __init__(self, mbcontext, pos_list, fiscal_sent_dir):
        # type: (MBEasyContext, List[int], Optional[unicode]) -> None
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list
        self.fiscal_sent_dir = fiscal_sent_dir

    def get_paid_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_paid_orders(ReportType.RealDate, initial_date, end_date, operator_id, None, report_pos)

    def get_paid_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_paid_orders(ReportType.BusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_paid_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_paid_orders(ReportType.SessionId, None, None, None, session_id, None)

    def get_voided_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_voided_orders(ReportType.RealDate, initial_date, end_date, operator_id, None, report_pos)

    def get_voided_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_voided_orders(ReportType.BusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_voided_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_voided_orders(ReportType.SessionId, None, None, None, session_id, None)

    def get_paid_orders_by_xml(self, initial_date, end_date):
        # type: (datetime, datetime) -> List[Order]
        orders = []  # type: List[Order]

        current_date = initial_date
        while current_date <= end_date:
            xml_directory = os.path.join(self.fiscal_sent_dir, "Enviados", current_date.strftime("%Y"), current_date.strftime("%m"), current_date.strftime("%d"))
            if os.path.exists(xml_directory):
                for entry in os.listdir(xml_directory):
                    try:
                        if entry.endswith(".xml"):
                            with open(os.path.join(xml_directory, entry), "rb") as xml_file:
                                xml_content = xml_file.read()
                            order = self._get_order_from_xml(entry, xml_content)
                            if order is not None:
                                orders.append(order)
                    except Exception as ex:
                        sys_log_exception("Fail to read xml: %s; Exception: %s" % (xml_directory, ex))

            current_date += timedelta(days=1)

        return orders

    def _get_paid_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            try:
                if report_type == ReportType.RealDate:
                    query = self._PaidOrdersByRealDateQuery
                    date_format = "%Y-%m-%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
                elif report_type == ReportType.BusinessPeriod:
                    query = self._PaidOrderByBusinessPeriod
                    date_format = "%Y%m%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
                else:
                    query = self._PaidOrderBySessionId
                    date_format = "%Y%m%d"
                    query = query.format(session_id)

                if (report_type == ReportType.RealDate or ReportType.BusinessPeriod) and operator_id is not None:
                    query += " and o.SessionId like '%user={0},%'".format(operator_id)

                all_orders = {}  # type: Dict[int, Order]
                order_with_payments = [(int(x.get_entry(0)),
                                        int(x.get_entry(1)),
                                        datetime.strptime(x.get_entry(2), date_format),
                                        float(x.get_entry(3)),
                                        int(x.get_entry(4)),
                                        float(x.get_entry(5)),
                                        float(x.get_entry(6)),
                                        float(x.get_entry(7))) for x in conn.select(query)]

                for order_tuple in order_with_payments:
                    order_id = order_tuple[0]
                    order_state = order_tuple[1]
                    order_date = order_tuple[2]
                    order_total = order_tuple[3]
                    donation_value = order_tuple[6]
                    change_amount = order_tuple[7]

                    if order_id in all_orders:
                        order = all_orders[order_id]
                    else:
                        order = Order(order_id, order_date, order_state, order_total, donation_value, [], None, change_amount)
                        all_orders[order_id] = order

                    tender_type = order_tuple[4]
                    tender_value = order_tuple[5]

                    order_tender = OrderTender(tender_type, tender_value)
                    order.tenders.append(order_tender)

                return list(all_orders.values())
            except:
                return list()

        report_pos_list = self.pos_list if report_pos is None else (report_pos, )
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    def _get_voided_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            if report_type == ReportType.RealDate:
                query = self._VoidedOrdersByRealDateQuery
                date_format = "%Y-%m-%d"
                query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
            elif report_type == ReportType.BusinessPeriod:
                query = self._VoidedOrdersByBusinessPeriod
                date_format = "%Y%m%d"
                query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
            else:
                query = self._VoidedOrdersBySessionId
                date_format = "%Y%m%d"
                query = query.format(session_id)

            if (report_type == ReportType.RealDate or report_type == ReportType.BusinessPeriod) and operator_id is not None:
                query += " and o.SessionId like '%user={0},%'".format(operator_id)

            order_with_payments = [(int(x.get_entry(0)),
                                    int(x.get_entry(1)),
                                    datetime.strptime(x.get_entry(2), date_format),
                                    float(x.get_entry(3)),
                                    float(x.get_entry(4)),
                                    x.get_entry(5)) for x in conn.select(query)]

            all_orders = []  # type: List[Order]
            for order_tuple in order_with_payments:
                order_id = order_tuple[0]
                order_state = order_tuple[1]
                order_date = order_tuple[2]
                order_total = order_tuple[3]
                donation_value = order_tuple[4]
                void_reason_id = order_tuple[5]

                order = Order(order_id, order_date, order_state, order_total, donation_value, [], void_reason_id, None)
                all_orders.append(order)

            return all_orders

        report_pos_list = self.pos_list if report_pos is None else (report_pos, )
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    def _get_order_from_xml(self, xml_file_name, xml_content):
        # type: (str, str) -> Optional[Order]
        if xml_content.find("<CFe>") >= 0:
            return self._get_order_from_sat_xml(xml_file_name, xml_content)
        elif xml_content.find("<NFe") >= 0:
            return self._get_order_from_nfce_xml(xml_content)
        else:
            return None

    @staticmethod
    def _get_order_from_sat_xml(xml_file_name, xml_content):
        parsed_xml = eTree.XML(xml_content)
        index1 = xml_file_name.find("_")
        index2 = xml_file_name.find("_", index1 + 1)
        order_id = int(xml_file_name[index1 + 1: index2])

        numero_nota = xml_file_name[:index1]

        data_nota = parsed_xml.find("infCFe/ide/dEmi").text
        hora_nota = parsed_xml.find("infCFe/ide/hEmi").text
        data_emissao = datetime.strptime(data_nota + hora_nota, "%Y%m%d%H%M%S")

        v_total = float(parsed_xml.find("infCFe/total/ICMSTot/vProd").text)

        tenders = []  # type: List[OrderTender]
        troco = parsed_xml.find("infCFe/pgto/vTroco")
        pgtos = parsed_xml.findall("infCFe/pgto/MP")
        for pgto in pgtos:
            c_mp = int(pgto.find("cMP").text)
            v_mp = float(pgto.find("vMP").text)

            if c_mp == 1:  # DINHEIRO
                tender_type = 0
            elif c_mp == 3:  # CREDITO:
                tender_type = 1
            elif c_mp == 4:  # DEBITO
                tender_type = 2
            else:
                tender_type = 99

            if tender_type == 0 and troco is not None:
                v_mp -= float(troco.text)
                troco = None

            tender = OrderTender(tender_type, v_mp)
            tenders.append(tender)

        order = Order(order_id, data_emissao, 5, v_total, 0, tenders, None)
        order.numero_nota = numero_nota

        return order

    @staticmethod
    def _get_order_from_nfce_xml(xml_content):
        nfe_namespace = "http://www.portalfiscal.inf.br/nfe"

        parsed_xml = eTree.XML(xml_content)
        c_nf = parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}cNF".format(nfe_namespace)).text
        n_serie = parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}serie".format(nfe_namespace)).text
        order_id = int(n_serie + c_nf)

        data_hora_nota = parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}dhEmi".format(nfe_namespace)).text
        data_emissao = iso8601.parse_date(data_hora_nota)

        v_total = float(parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}total/{{{0}}}ICMSTot/{{{0}}}vProd".format(nfe_namespace)).text)

        tenders = []  # type: List[OrderTender]
        pgtos = parsed_xml.findall("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}pag".format(nfe_namespace))
        for pgto in pgtos:
            t_pag = int(pgto.find("{{{0}}}tPag".format(nfe_namespace)).text)
            v_pag = float(pgto.find("{{{0}}}vPag".format(nfe_namespace)).text)

            if t_pag == 1:
                tender_type = 0  # DINHEIRO
            elif t_pag == 3:
                tender_type = 1  # CREDITO
            elif t_pag == 4:
                tender_type = 2  # DEBITO
            else:
                tender_type = 99  # OUTROS

            tender = OrderTender(tender_type, v_pag)
            tenders.append(tender)

        order = Order(order_id, data_emissao, 5, v_total, 0, tenders, None)

        return order

    _PaidOrdersByRealDateQuery = \
"""select o.OrderId, o.StateId, od.OrderDate, o.TotalGross, ot.TenderId, ot.TenderAmount, coalesce(ocp.Value, 0), coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
inner join
(
    -- Busca as Orders do dia que estamos interessadosh
    select OrderId, strftime('%Y-%m-%d', Value, 'localtime') OrderDate
    from OrderCustomProperties
    where key = 'FISCALIZATION_DATE' and strftime('%Y-%m-%d', Value, 'localtime') >= '{0}' and strftime('%Y-%m-%d', Value, 'localtime') <= '{1}'
) od
on o.OrderId = od.OrderId
left join OrderCustomProperties ocp
on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
where o.StateId = 5;"""

    _VoidedOrdersByRealDateQuery = \
"""select o.OrderId, o.StateId, od.OrderDate, coalesce(o.TotalGross, 0), coalesce(ocp.Value, 0), vrs.Value as VoidReason
from Orders o
inner join
(
    -- Busca as Orders do dia que estamos interessados
    select OrderId, OrderDate
    from
    (
        -- Busca a última data que as Orders foram totalizadas
        select OrderId, strftime('%Y-%m-%d', max(Timestamp) , 'localtime') OrderDate
        from
        (
            select OrderId, StateId, Timestamp from OrderStateHistory
            where strftime('%Y-%m-%d', Timestamp, 'localtime') > strftime('%Y-%m-%d', '{0}' , '-1 day') and strftime('%Y-%m-%d', Timestamp, 'localtime') < strftime('%Y-%m-%d', '{1}' , '+1 day')
        )
        where StateId = 4
        group by OrderId
    ) a where a.OrderDate >= '{0}' and a.OrderDate <= '{1}'
) od
on o.OrderId = od.OrderId
left join OrderCustomProperties ocp
on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_ID'
where o.StateId = 4;"""

    _PaidOrderByBusinessPeriod = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, ot.TenderAmount, coalesce(ocp.Value, 0), coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
left join OrderCustomProperties ocp
on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
where o.BusinessPeriod >= '{0}' and o.BusinessPeriod <= '{1}' and o.StateId = 5;"""

    _VoidedOrdersByBusinessPeriod = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, coalesce(o.TotalGross, 0), coalesce(ocp.Value, 0), vrs.Value as VoidReason
from Orders o
left join OrderCustomProperties ocp
on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_ID'
where o.BusinessPeriod >= '{0}'  and o.BusinessPeriod <= '{1}' and o.StateId = 4;"""

    _PaidOrderBySessionId = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, ot.TenderAmount, coalesce(ocp.Value, 0), coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
left join OrderCustomProperties ocp
on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
where o.SessionId = '{0}' and o.StateId = 5;"""

    _VoidedOrdersBySessionId = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, coalesce(o.TotalGross, 0), coalesce(ocp.Value, 0), vrs.Value as VoidReason
from Orders o
left join OrderCustomProperties ocp
on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_ID'
where o.SessionId = '{0}' and o.StateId = 4;"""
