# encoding: utf-8
import os
import iso8601
from helper import MwOrderStatus
from old_helper import BaseRepository
from msgbus import MBEasyContext
from ..model import Order, OrderTender
from persistence import Connection
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from xml.etree import cElementTree as eTree
from systools import sys_log_exception


class OrderRepository(BaseRepository):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, mbcontext, pos_list, fiscal_sent_dir):
        # type: (MBEasyContext, List[int], unicode) -> None
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list
        self.fiscal_sent_dir = fiscal_sent_dir

    def get_paid_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos, session_id=None):
        # type: (datetime, datetime, Optional[unicode], Optional[unicode]) -> List[Order]
        return self._get_paid_orders(self.TypeRealDate, initial_date, end_date, operator_id, session_id, report_pos)

    def get_paid_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_paid_orders(self.TypeBusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_voided_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos, session_id=None):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_voided_orders(self.TypeRealDate, initial_date, end_date, operator_id, session_id, report_pos)

    def get_voided_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_voided_orders(self.TypeBusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_paid_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_paid_orders(self.TypeSessionId, None, None, None, session_id, None)

    def get_voided_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_voided_orders(self.TypeSessionId, None, None, None, session_id, None)

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

    def get_voided_orders_by_xml(self, initial_date, end_date):
        # type: (datetime, datetime) -> List[Order]
        return []

    def get_hourly_sale(self, report_pos, initial_date, end_date, operator):
        # type: (unicode, Optional[datetime], Optional[datetime]) -> List[object]
        def inner_func(conn):
            # type: (Connection) -> List[object]
            try:
                initial_date_formatted = initial_date[:4] + '-' + initial_date[4:6] + '-' + initial_date[6:]
                end_date_formatted = end_date[:4] + '-' + end_date[4:6] + '-' + end_date[6:]
                query = self._QueryHourlySale.format(initial_date_formatted, end_date_formatted, operator)

                order_by_hour = [(str(x.get_entry(0)),
                                 str(x.get_entry(1)),
                                 int(x.get_entry(2)),
                                 int(x.get_entry(3)),
                                 float(x.get_entry(4)),
                                 int(x.get_entry(5))) for x in conn.select(query)]

                return list(order_by_hour)
            except Exception, ex:
                sys_log_exception('erro: %s' % ex)
                return list()

        report_pos_list = self.pos_list if report_pos is None else (report_pos,)
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    def _get_paid_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            try:
                if operator_id is not None:
                    current_session_id = "user={}".format(operator_id)
                else:
                    current_session_id = session_id if session_id is not None and session_id != 'None' else ''

                if report_type == self.TypeRealDate:
                    query = self._PaidOrdersByRealDateQuery
                    date_format = "%Y-%m-%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format), current_session_id)
                elif report_type == self.TypeBusinessPeriod:
                    query = self._PaidOrderByBusinessPeriod
                    date_format = "%Y%m%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format), current_session_id)
                else:
                    query = self._PaidOrderBySessionId
                    date_format = "%Y%m%d"
                    query = query.format(session_id)

                all_orders = {}  # type: Dict[int, Order]
                order_with_payments = [(int(x.get_entry(0)),
                                        int(x.get_entry(1)),
                                        datetime.strptime(x.get_entry(2), date_format),
                                        float(x.get_entry(3)),
                                        int(x.get_entry(4)),
                                        float(x.get_entry(5)),
                                        float(x.get_entry(6)),
                                        x.get_entry(7),
                                        x.get_entry(8),
                                        x.get_entry(9),
                                        x.get_entry(10),
                                        x.get_entry(11)) for x in conn.select(query)]

                for order_tuple in order_with_payments:
                    order_id = order_tuple[0]
                    order_state = order_tuple[1]
                    order_date = order_tuple[2]
                    order_total = order_tuple[3]
                    donation_value = order_tuple[6]
                    discount_value = float(order_tuple[7]) if order_tuple[7] else None
                    tip_value = float(order_tuple[8]) if order_tuple[8] else None
                    sale_type = int(order_tuple[9])
                    table_id = order_tuple[10]
                    delivery_originator = order_tuple[11]

                    if order_id in all_orders:
                        order = all_orders[order_id]
                    else:
                        order = Order(order_id, order_date, order_state, order_total, donation_value, [], None, discount_value, tip_value, sale_type, table_id, None, delivery_originator)
                        all_orders[order_id] = order

                    tender_type = order_tuple[4]
                    tender_value = order_tuple[5]

                    order_tender = OrderTender(tender_type, tender_value)
                    order.tenders.append(order_tender)
                return list(all_orders.values())
            except Exception as _:
                return list({"error": "error"}.values())

        report_pos_list = self.pos_list if report_pos is None else (report_pos,)
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    def _get_voided_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            try:
                if operator_id is not None:
                    current_session_id = "user={}".format(operator_id)
                else:
                    current_session_id = session_id if session_id is not None and session_id != 'None' else ''

                if report_type == self.TypeRealDate:
                    query = self._VoidedOrdersByRealDateQuery
                    date_format = "%Y-%m-%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format), current_session_id)
                elif report_type == self.TypeBusinessPeriod:
                    query = self._VoidedOrdersByBusinessPeriod
                    date_format = "%Y%m%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format), current_session_id)
                else:
                    query = self._VoidedOrdersBySessionId
                    date_format = "%Y%m%d"
                    query = query.format(session_id)

                order_with_payments = [(int(x.get_entry(0)),
                                        int(x.get_entry(1)),
                                        datetime.strptime(x.get_entry(2), date_format),
                                        float(x.get_entry(3)),
                                        float(x.get_entry(4)),
                                        x.get_entry(5),
                                        x.get_entry(6),
                                        x.get_entry(7),
                                        x.get_entry(8),
                                        x.get_entry(9),
                                        x.get_entry(10)) for x in conn.select(query)]

                all_orders = []  # type: List[Order]
                for order_tuple in order_with_payments:
                    order_id = order_tuple[0]
                    order_state = order_tuple[1]
                    order_date = order_tuple[2]
                    order_total = order_tuple[3]
                    donation_value = order_tuple[4]
                    void_reason_id = order_tuple[5]
                    discount_value = float(order_tuple[6]) if order_tuple[6] else None
                    tip_value = float(order_tuple[7]) if order_tuple[7] else None
                    sale_type = int(order_tuple[8])
                    table_id = order_tuple[9]
                    delivery_originator = order_tuple[10]

                    order = Order(order_id, order_date, order_state, order_total, donation_value, [], void_reason_id, discount_value, tip_value, sale_type, table_id, None, delivery_originator)
                    all_orders.append(order)

                return all_orders
            except:
                return list({"error": "error"}.values())

        report_pos_list = self.pos_list if report_pos is None else (report_pos, )
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    def _get_order_from_xml(self, xml_file_name, xml_content):
        if xml_content.find("<CFe>") >= 0:
            return self._get_order_from_sat_xml(xml_file_name, xml_content)
        elif xml_content.find("<NFe") >= 0:
            return self._get_order_from_nfce_xml(xml_content)
        else:
            return None

    def _get_order_from_sat_xml(self, xml_file_name, xml_content):
        parsed_xml = eTree.XML(xml_content)
        index1 = xml_file_name.find("_")
        index2 = xml_file_name.find("_", index1 + 1)
        order_id = int(xml_file_name[index1 + 1: index2])

        numero_nota = xml_file_name[:index1]

        data_nota = parsed_xml.find("infCFe/ide/dEmi").text
        hora_nota = parsed_xml.find("infCFe/ide/hEmi").text
        data_emissao = datetime.strptime(data_nota + hora_nota, "%Y%m%d%H%M%S")

        v_desc = float(parsed_xml.find("infCFe/total/ICMSTot/vDesc").text)
        v_total = round(float(parsed_xml.find("infCFe/total/ICMSTot/vProd").text) - v_desc, 2)

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

            if troco is not None:
                v_mp = round(v_mp - float(troco.text), 2)
                troco = None

            tender = OrderTender(tender_type, v_mp)
            tenders.append(tender)

        order = Order(order_id, data_emissao, 5, v_total, 0, tenders, None, v_desc, None, None, None, None)
        order.numero_nota = numero_nota

        return order

    def _get_order_from_nfce_xml(self, xml_content):
        nfe_namespace = "http://www.portalfiscal.inf.br/nfe"

        parsed_xml = eTree.XML(xml_content)
        c_nf = parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}cNF".format(nfe_namespace)).text
        n_serie = parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}serie".format(nfe_namespace)).text
        order_id = int(n_serie + c_nf)

        data_hora_nota = parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}dhEmi".format(nfe_namespace)).text
        data_emissao = iso8601.parse_date(data_hora_nota)

        v_desc = float(parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}total/{{{0}}}ICMSTot/{{{0}}}vDesc".format(nfe_namespace)).text)
        v_total = round(float(parsed_xml.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}total/{{{0}}}ICMSTot/{{{0}}}vProd".format(nfe_namespace)).text) - v_desc, 2)

        tenders = []  # type: List[OrderTender]
        pgtos = parsed_xml.findall("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}pag".format(nfe_namespace))[0]
        v_troco = pgtos.find(".//{{{0}}}vTroco".format(nfe_namespace))
        v_troco = float(v_troco.text) if v_troco is not None else 0.0

        for pgto in pgtos:
            if "vTroco" in pgto.tag:
                continue

            t_pag = int(pgto.find(".//{{{0}}}tPag".format(nfe_namespace)).text)
            v_pag = float(pgto.find(".//{{{0}}}vPag".format(nfe_namespace)).text)

            if t_pag == 1:  # DINHEIRO
                tender_type = 0
            elif t_pag == 3:  # CREDITO:
                tender_type = 1
            elif t_pag == 4:  # DEBITO
                tender_type = 2
            else:
                tender_type = 99

            if v_troco != 0.0:
                v_pag = round(v_pag - v_troco, 2)
                v_troco = 0.0

            tender = OrderTender(tender_type, v_pag)
            tenders.append(tender)

        order = Order(order_id, data_emissao, 5, v_total, 0, tenders, None, v_desc, None, None, None, None)

        return order

    def get_payments_by_order(self, paid_orders):
        def inner_func(conn):
            order_list = map(lambda order: order.order_id, paid_orders)
            order_list = ','.join(map(str, order_list))
            query = _GetPaymentsByOrders
            query = query.format(order_list)

            return [(int(x.get_entry(0)), float(x.get_entry(1)), int(x.get_entry(2))) for x in conn.select(query)]

        ret = self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

        grouped_payments_by_order = {}
        for tender_type in ret:
            tender_id = tender_type[0]
            tender_grouped_value = tender_type[1]
            tender_grouped_quantity = tender_type[2]

            if tender_id not in grouped_payments_by_order:
                grouped_payments_by_order[tender_id] = {'value': tender_grouped_value,
                                                        'quantity': tender_grouped_quantity,
                                                        'id': tender_grouped_quantity}
            else:
                grouped_payments_by_order[tender_id]['value'] += tender_grouped_value
                grouped_payments_by_order[tender_id]['quantity'] += tender_grouped_quantity

        return grouped_payments_by_order

    def get_change_sum(self, initial_date, end_date):
        def inner_func(conn):
            query = _GetChangeAmountSum.format(initial_date, end_date)
            return [(x.get_entry(0), float(x.get_entry(1))) for x in conn.select(query)]

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    def get_tender_details(self, paid_orders):
        def inner_func(conn):
            all_orders_id = ",".join([str(x.order_id) for x in paid_orders])
            query = """select tenderid, tenderamount, tenderdetail from ordertender where orderid in ({})""".format(all_orders_id)
            return [(x.get_entry("TenderId"),
                     x.get_entry("TenderAmount"),
                     x.get_entry("TenderDetail")) for x in conn.select(query)]

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    def get_opened_orders(self, report_type, session_id=None, initial_date=None, end_date=None, operator_id=None):
        def inner_func(conn):
            query = """
            SELECT o.OrderId 
                FROM Orders o 
                JOIN ServiceOrders so ON so.OrderId == o.OrderId 
            WHERE o.StateId = {}""".format(MwOrderStatus.STORED.value)

            if operator_id:
                query += " and so.UserId = {}".format(operator_id)

            if report_type == self.TypeSessionId:
                if not session_id:
                    return []
                query += " and SessionId like '%{}%';".format(session_id)
            else:
                if not initial_date or not end_date:
                    return []
                date_format = "%Y%m%d"
                formatted_initial_date = initial_date.strftime(date_format)
                formatted_end_date = end_date.strftime(date_format)
                if report_type == self.TypeBusinessPeriod:
                    query += " and substr(SessionID, instr(SessionID, 'period=')+7) >= '{0}' " \
                             " and substr(SessionID, instr(SessionID, 'period=')+7) <= '{1}';"\
                        .format(formatted_initial_date, formatted_end_date)
                elif report_type == self.TypeRealDate:
                    query += " and strftime('%Y%m%d', CreatedAt, 'localtime') >= '{}' " \
                             " and strftime('%Y%m%d', CreatedAt, 'localtime') <= '{}';"\
                        .format(formatted_initial_date, formatted_end_date)

            return [row.get_entry("OrderId") for row in conn.select(query)]

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    _PaidOrdersByRealDateQuery = \
"""select o.OrderId, o.StateId, od.OrderDate, o.TotalGross, ot.TenderId, sum(ot.TenderAmount - coalesce(ot.ChangeAmount, 0)), coalesce(ocp.Value, 0), o.DiscountAmount, o.Tip, o.SaleType, tab.value, coalesce(dly.Value, sn.Value)
    from Orders o
    inner join OrderTender ot on o.OrderId = ot.OrderId
    inner join (
        select OrderId, strftime('%Y-%m-%d', Value, 'localtime') OrderDate
        from OrderCustomProperties
        where key = 'FISCALIZATION_DATE' 
            and strftime('%Y-%m-%d', Value, 'localtime') >= '{0}' 
            and strftime('%Y-%m-%d', Value, 'localtime') <= '{1}'
    ) od on o.OrderId = od.OrderId
    left join OrderCustomProperties ocp on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
    left join OrderCustomProperties tab on tab.OrderId = o.OrderId and tab.Key = 'TABLE_ID'
    left join OrderCustomProperties dly on dly.OrderId = o.OrderId and dly.Key = 'ORIGINATOR'
    left join OrderCustomProperties sn on sn.OrderId = o.OrderId and sn.Key = 'STORE_NAME'
    where o.StateId = 5 and SessionId like '%{2}%'
    group by ot.orderid"""

    _VoidedOrdersByRealDateQuery = \
"""select o.OrderId, o.StateId, od.OrderDate, coalesce(o.TotalGross, 0), coalesce(ocp.Value, 0), vrs.Value as VoidReason, o.DiscountAmount, o.Tip, o.SaleType, tab.value, coalesce(dly.Value, sn.Value)
    from Orders o
    inner join (
        select OrderId, OrderDate 
        from (
            select OrderId, strftime('%Y-%m-%d', max(Timestamp) , 'localtime') OrderDate
            from (
                select OrderId, StateId, Timestamp from OrderStateHistory 
                where strftime('%Y-%m-%d', Timestamp, 'localtime') > strftime('%Y-%m-%d', '{0}' , '-1 day') 
                  and strftime('%Y-%m-%d', Timestamp, 'localtime') < strftime('%Y-%m-%d', '{1}' , '+1 day')
            )
            where StateId = 4
            group by OrderId
        ) a where a.OrderDate >= '{0}' and a.OrderDate <= '{1}'
    ) od on o.OrderId = od.OrderId
    left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_ID'
    left join OrderCustomProperties ocp on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
    left join OrderCustomProperties tab on tab.OrderId = o.OrderId and tab.Key = 'TABLE_ID'
    left join OrderCustomProperties dly on dly.OrderId = o.OrderId and dly.Key = 'ORIGINATOR'
    left join OrderCustomProperties sn on sn.OrderId = o.OrderId and sn.Key = 'STORE_NAME'
    where o.StateId = 4 and SessionId like '%{2}%'
    group by o.orderid"""

    _PaidOrderByBusinessPeriod = \
"""select o.OrderId, o.StateId, substr(o.SessionID, instr(o.SessionID, 'period=')+7), o.TotalGross, ot.TenderId, sum(ot.TenderAmount - coalesce(ot.ChangeAmount, 0)), coalesce(ocp.Value, 0), o.DiscountAmount, o.Tip, o.SaleType, tab.value, coalesce(dly.Value, sn.Value)
    from Orders o
    inner join OrderTender ot on o.OrderId = ot.OrderId
    left join OrderCustomProperties ocp on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
    left join OrderCustomProperties tab on tab.OrderId = o.OrderId and tab.Key = 'TABLE_ID'
    left join OrderCustomProperties dly on dly.OrderId = o.OrderId and dly.Key = 'ORIGINATOR'
    left join OrderCustomProperties sn on sn.OrderId = o.OrderId and sn.Key = 'STORE_NAME'
    where o.StateId = 5 and SessionId like '%{2}%'
        and substr(o.SessionID, instr(o.SessionID, 'period=')+7) >= '{0}'
        and substr(o.SessionID, instr(o.SessionID, 'period=')+7) <= '{1}'
    group by o.orderid"""

    _VoidedOrdersByBusinessPeriod = \
"""select o.OrderId, o.StateId, substr(o.SessionID, instr(o.SessionID, 'period=')+7), coalesce(o.TotalGross, 0), coalesce(ocp.Value, 0), vrs.Value, o.DiscountAmount, o.Tip, o.SaleType, tab.value, coalesce(dly.Value, sn.Value)
    from Orders o
    left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_ID'
    left join OrderCustomProperties ocp on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
    left join OrderCustomProperties tab on tab.OrderId = o.OrderId and tab.Key = 'TABLE_ID'
    left join OrderCustomProperties dly on dly.OrderId = o.OrderId and dly.Key = 'ORIGINATOR'
    left join OrderCustomProperties sn on sn.OrderId = o.OrderId and sn.Key = 'STORE_NAME'
    where o.StateId = 4 and SessionId like '%{2}%'
        and substr(o.SessionID, instr(o.SessionID, 'period=')+7) >= '{0}'
        and substr(o.SessionID, instr(o.SessionID, 'period=')+7) <= '{1}'
    group by o.orderid"""

    _PaidOrderBySessionId = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, sum(ot.TenderAmount - coalesce(ot.ChangeAmount, 0)), coalesce(ocp.Value, 0), o.DiscountAmount, o.Tip, o.SaleType, coalesce(dly.Value, sn.Value)
    from Orders o
    inner join OrderTender ot on o.OrderId = ot.OrderId
    left join OrderCustomProperties ocp on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
    left join OrderCustomProperties tab on tab.OrderId = o.OrderId and tab.Key = 'TABLE_ID'
    left join OrderCustomProperties dly on dly.OrderId = o.OrderId and dly.Key = 'ORIGINATOR'
    left join OrderCustomProperties sn on sn.OrderId = o.OrderId and sn.Key = 'STORE_NAME'
    where o.SessionId = '{0}' and o.StateId = 5
    group by o.orderid"""

    _VoidedOrdersBySessionId = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, coalesce(o.TotalGross, 0), coalesce(ocp.Value, 0), vrs.Value as VoidReason, o.DiscountAmount, o.Tip, o.SaleType, coalesce(dly.Value, sn.Value)
    from Orders o
    left join OrderCustomProperties ocp on ocp.OrderId = o.OrderId and ocp.Key = 'DONATION_VALUE'
    left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_ID'
    left join OrderCustomProperties tab on tab.OrderId = o.OrderId and tab.Key = 'TABLE_ID'
    left join OrderCustomProperties dly on dly.OrderId = o.OrderId and dly.Key = 'ORIGINATOR'
    left join OrderCustomProperties sn on sn.OrderId = o.OrderId and sn.Key = 'STORE_NAME'
    where o.SessionId = '{0}' and o.StateId = 4
    group by o.orderid"""

    _QueryHourlySale = """
SELECT storetype, 
       orderdate, 
       hora, 
       minuto, 
       SUM(totalgross) total,
	   count(1) total_transcations
FROM   (SELECT ( CASE 
                   WHEN distributionpoint == 'DT' THEN 'DT' 
                   ELSE CASE WHEN distributionpoint == 'KK' THEN 'KK'
				   ELSE 'STORE' 
				  END 
                 END )                                      StoreType, 
               Strftime('%Y-%m-%d', orderdate, 'localtime') OrderDate, 
               Strftime('%H', orderdate, 'localtime')       HORA, 
               ( CASE 
                   WHEN Cast(Strftime('%M', orderdate, 'localtime')AS INT) > 29 
                 THEN 
                   '30' 
                   ELSE '00' 
                 END )                                      AS MINUTO, 
               o.totalgross 
        FROM   orders o 
               inner join ordertender ot 
                       ON o.orderid = ot.orderid 
               inner join ( 
                          -- Busca as Orders do dia que estamos interessadosh  
                          SELECT orderid, 
                                 value OrderDate 
                           FROM   ordercustomproperties 
                           WHERE  KEY = 'FISCALIZATION_DATE' 
                                  AND Strftime('%Y-%m-%d', value, 'localtime') 
                                      >= 
                                      '{}' 
                                  AND Strftime('%Y-%m-%d', value, 'localtime') 
                                      <= 
                                      '{}') 
                                                            od 
                       ON o.orderid = od.orderid 
               left join ordercustomproperties ocp 
                      ON ocp.orderid = o.orderid 
                         AND ocp.KEY = 'DONATION_VALUE' 
        WHERE  o.stateid = 5 and o.SessionId like '%user={}%') a 
GROUP  BY storetype, 
          orderdate, 
          hora, 
          minuto  """


_GetPaymentsByOrders = \
"""SELECT TenderId, SUM(COALESCE(TenderAmount, 0) - COALESCE(ChangeAmount, 0)) as Amount, COUNT(OrderId)
FROM OrderTender
WHERE OrderId in ({0})
GROUP BY TenderId"""


_GetChangeAmountSum = \
"""select o.sessionid, sum(ot.changeamount)
from orders o
join ordertender ot on o.orderid = ot.orderid
join ordercustomproperties ocp on ocp.orderid = o.orderid
where ot.changeamount is not null
    and key = 'FISCALIZATION_DATE' and strftime('%Y%m%d', Value, 'localtime') >= '{0}' 
    and strftime('%Y%m%d', Value, 'localtime') <= '{1}'
group by o.sessionid
"""
