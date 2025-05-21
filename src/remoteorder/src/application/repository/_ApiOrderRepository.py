# -*- coding: utf-8 -*-

import logging

from application.customexception import InvalidSonException, OrderValidationError
from application.mwmodel import MwOrder, MwOrderItem, MwOrderCustomProperty
from msgbus import MBEasyContext, TK_POS_EXECUTEACTION
from mwhelper import BaseRepository
from persistence import Connection
from typing import List, Dict, Union, Tuple, Optional

logger = logging.getLogger("RemoteOrder")


class ApiOrderRepository(BaseRepository):
    def __init__(self, mb_context, pos_id, last_orders_first, mandatory_logistic_for_integration):
        # type: (MBEasyContext, int, bool, bool) -> None
        super(ApiOrderRepository, self).__init__(mb_context)
        self.mb_context = mb_context
        self.pos_id = pos_id
        self.last_orders_first = last_orders_first
        self.mandatory_logistic_for_integration = mandatory_logistic_for_integration

    def get_order_by_remote_id(self, remote_order_id):
        # type: (int) -> Union[MwOrder, None]
        query = """select o.OrderId, o.StateId, ocp.Key, ocp.Value, oi.LineNumber, oi.ItemId, oi.PartCode, oi.Level, oi.OrderedQty, o.TotalGross, o.BusinessPeriod
                        from Orders o
                        inner join OrderCustomProperties ocp
                        on o.OrderId = ocp.OrderId
                        left join OrderItem oi
                        on o.OrderId = oi.OrderId
                        where ocp.Key = "REMOTE_ORDER_ID" and ocp.Value = '{0}'""".format(remote_order_id)

        order_list = self._get_order_list(query)
        if len(order_list) > 0:
            return order_list[0]
        else:
            return None

    def is_order_produced(self, order_id="", remote_order_id=""):
        # type: (Optional[str], Optional[str]) -> bool

        def inner_func(conn):
            # type: (Connection) -> bool
            query = """
            select o.OrderId
            from Orders o
                inner join OrderCustomProperties ocp on o.OrderId = ocp.OrderId
            where o.StateId = 5
                and (o.OrderId = '{0}'
                or o.OrderId in (select OrderId
                                 from OrderCustomProperties ocp
                                 where ocp.Key = 'REMOTE_ORDER_ID' and ocp.Value = '{1}'))
            """.format(order_id, remote_order_id)

            return len([x.get_entry(0) for x in conn.select(query)]) > 0

        return self.execute_with_connection(inner_func, db_name=str(self.pos_id))

    def get_remote_order_info(self, order_id):
        # type: (int) -> (str, str)

        def inner_func(conn):
            query = """select  remote_id.Value as RemoteOrderId,
                               partner.Value as Partner     
                       from Orders o
                           left join OrderCustomProperties remote_id on o.OrderId = remote_id.OrderId and remote_id.Key = 'REMOTE_ORDER_ID'
                           left join OrderCustomProperties partner on o.OrderId = partner.OrderId and partner.Key = 'PARTNER'
                       where o.OrderId = '{}'""".format(order_id)

            all_data = [(x.get_entry("RemoteOrderId"),
                         x.get_entry("Partner")) for x in conn.select(query)]
            if len(all_data) > 0:
                remote_order_id, partner = all_data[0]
                return order_id, remote_order_id, partner
            return None
        return self.execute_with_connection(inner_func, db_name=str(self.pos_id))

    def get_order(self, local_order_id):
        # type: (int) -> Union[MwOrder, None]
        query = """select o.OrderId, o.StateId, ocp.Key, ocp.Value, oi.LineNumber, oi.ItemId, oi.PartCode, oi.Level, oi.OrderedQty, o.TotalGross, o.BusinessPeriod
                        from Orders o
                        inner join OrderCustomProperties ocp
                        on o.OrderId = ocp.OrderId
                        inner join OrderItem oi
                        on o.OrderId = oi.OrderId
                        where o.OrderId = {0}""".format(local_order_id)

        order_list = self._get_order_list(query)
        if len(order_list) > 0:
            return order_list[0]
        else:
            return None

    def get_stored_orders(self, return_paid_orders):
        mandatory_logistic_query = ''
        if self.mandatory_logistic_for_integration:
            mandatory_logistic_query = """
            and ocp.Key = 'LOGISTIC_INTEGRATION_STATUS' and ocp.Value in ('Received', 'Confirmed', 'Finished')
            """

        query = """
                select o.OrderId, 
                       o.StateId, 
                       ocp.Key, 
                       ocp.Value, 
                       oi.LineNumber, 
                       oi.ItemId, 
                       oi.PartCode, 
                       oi.Level, 
                       oi.OrderedQty, 
                       o.TotalGross, 
                       o.BusinessPeriod
                from Orders o
                inner join OrderCustomProperties ocp
                on o.OrderId = ocp.OrderId
                inner join OrderItem oi
                on o.OrderId = oi.OrderId
                where o.OrderId in (
                    select distinct o.OrderId
                    from Orders o
                    inner join OrderCustomProperties ocp
                    on o.OrderId = ocp.OrderId
                    where (o.StateId in ({}))
                    and ocp.OrderId in (
                        select OrderId from OrderCustomProperties where Key = 'PICKUP_TYPE' and VALUE in ('delivery', 'eat_in', 'take_out', 'drive_thru', 'eat_out')
                    )
                      and ocp.OrderId not in (
                        select OrderId from OrderCustomProperties where Key = 'PARTNER' and LOWER(VALUE) = 'app'
                    )
                      and ocp.OrderId not in (
                        select OrderId from OrderCustomProperties where Key in ('CONFIRM_DELIVERY_PAYMENT', 'DELIVERY_ERROR_TYPE')
                    )
                    and o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')
                    {}
                    order by o.CreatedAt DESC LIMIT 50
                )
                """.format(self.get_formatted_order_status(return_paid_orders), mandatory_logistic_query)

        return self._get_order_list(query)

    @staticmethod
    def get_formatted_order_status(return_paid_orders):
        if return_paid_orders:
            return '2, 5'

        return '2'

    def get_error_orders(self):
        query = """select o.OrderId, o.StateId, ocp.Key, ocp.Value, oi.LineNumber, oi.ItemId, oi.PartCode, oi.Level, oi.OrderedQty, o.TotalGross, o.BusinessPeriod
                from Orders o
                inner join OrderCustomProperties ocp
                on o.OrderId = ocp.OrderId
                left join OrderItem oi
                on o.OrderId = oi.OrderId
                where (o.StateId = 2)
                and ocp.OrderId in (
                  select OrderId from OrderCustomProperties where Key = 'PICKUP_TYPE' and VALUE in ('delivery', 'eat_in', 'take_out')
                )
                and ocp.OrderId not in (
                  select OrderId from OrderCustomProperties where Key = 'PARTNER' and LOWER(VALUE) = 'app'
                )
                and ocp.OrderId in (
                  SELECT OrderId FROM OrderCustomProperties WHERE Key = 'DELIVERY_ERROR_TYPE'
                ) and o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')"""
        return self._get_order_list(query)

    def get_confirmed_orders(self):
        query = """
        select o.OrderId, o.StateId, ocp.Key, ocp.Value, oi.LineNumber, oi.ItemId, oi.PartCode, oi.Level, oi.OrderedQty, o.TotalGross, o.BusinessPeriod
        from Orders o
        inner join OrderCustomProperties ocp
        on o.OrderId = ocp.OrderId
        left join OrderItem oi
        on o.OrderId = oi.OrderId
        where o.OrderId in (
            select distinct o.OrderId
            from Orders o
            inner join OrderCustomProperties ocp on o.OrderId = ocp.OrderId
            where (o.StateId in (2, 4 ,5))
            and (ocp.OrderId in (select OrderId from OrderCustomProperties where Key = 'PICKUP_TYPE' and VALUE in ('delivery', 'eat_in', 'take_out'))
            and ocp.OrderId not in (select OrderId from OrderCustomProperties where Key = 'PARTNER' and LOWER(VALUE) = 'app')
            and ocp.OrderId in (select OrderId from OrderCustomProperties where Key = 'CONFIRM_DELIVERY_PAYMENT')
            or ocp.OrderId in (select OrderId from OrderCustomProperties where Key = 'VOID_REASON_ID')
            )
            and o.BusinessPeriod >= strftime('%Y%m%d', datetime('now', '-1 days'), 'localtime')
            order by o.CreatedAt DESC LIMIT 50
        )"""

        return self._get_order_list(query)

    def get_order_id_by_logistic_id(self, logistic_id):
        # type: (str) -> Union[int, None]

        def inner_func(conn):
            query = """
            SELECT o.OrderId
            FROM Orders o
            INNER JOIN OrderCustomProperties ocp ON o.OrderId = ocp.OrderId
            where ocp.Key = "LOGISTIC_ID" and ocp.Value = '{0}'
            """.format(logistic_id)

            for x in conn.select(query):
                return x.get_entry("OrderId")

            return None

        return self.execute_with_connection(inner_func, db_name=int(self.pos_id))

    def reprint_delivery_order(self, order_id):
        self.mb_context.MB_EasySendMessage('POS%s' % self.pos_id, token=TK_POS_EXECUTEACTION, format=2, data='\0'.join(['doReprintOrder', str(self.pos_id), str(order_id)]))

    def order_exists(self, order_id):
        # type: (int) -> bool
        def inner_func(conn):
            # type: (Connection) -> bool
            cursor = conn.select("select count(1) from Orders where OrderId = {0}".format(order_id))
            if cursor.rows() != 1:
                raise Exception(u"Internal error, the query should return at exactly one row")

            row = cursor.get_row(0)

            count = int(row.get_entry(0))
            return count > 0

        return self.execute_with_connection(inner_func, db_name=str(self.pos_id))

    def _get_order_list(self, query):
        # type: (unicode) -> List[MwOrder]
        def inner_func(conn):
            # type: (Connection) -> List[MwOrder]
            all_data = [(x.get_entry(0),
                         x.get_entry(1),
                         x.get_entry(2),
                         x.get_entry(3),
                         x.get_entry(4),
                         x.get_entry(5),
                         x.get_entry(6),
                         x.get_entry(7),
                         x.get_entry(8),
                         x.get_entry(9),
                         x.get_entry(10)) for x in conn.select(query)]

            data_grouped_by_order_id = {}  # type: Dict[int, List]
            for data in all_data:
                order_id = int(data[0])

                if order_id in data_grouped_by_order_id:
                    order_id_info = data_grouped_by_order_id[order_id]
                else:
                    order_id_info = []
                    data_grouped_by_order_id[order_id] = order_id_info

                order_id_info.append(data[1:])

            all_orders = []  # type: List[MwOrder]
            for order_id in data_grouped_by_order_id.keys():
                order_data = data_grouped_by_order_id[order_id]

                order_state = int(order_data[0][0])
                order_total = float(order_data[0][8] or 0)
                business_period = order_data[0][9]

                custom_property_dict = {}  # type: Dict[unicode, unicode]
                order_item_dict = {}  # type: Dict[Tuple[int, unicode]: Tuple[int, int, int]]
                for data in order_data:
                    custom_key = unicode(data[1], "utf-8")

                    if custom_key not in custom_property_dict:
                        custom_property_dict[custom_key] = unicode(data[2], "utf-8")
                    if data[5] is not None:
                        part_code = int(data[5])
                        context = unicode(data[4], "utf-8")
                        line_number = int(data[3])
                        order_item_key = (line_number, part_code, context)

                        if order_item_key not in order_item_dict:
                            line_number = int(data[3])
                            level = int(data[6])
                            ordered_qty = int(data[7]) if data[7] is not None and data[7] != 'NULL' else None
                            order_item_dict[order_item_key] = (line_number, level, ordered_qty)

                order = MwOrder()
                order.id = order_id
                order.total = order_total
                order.status = order_state
                order.business_period = business_period
                order.custom_properties = {}
                for custom_property_key in custom_property_dict:
                    custom_property = MwOrderCustomProperty()
                    custom_property.key = custom_property_key
                    custom_property.value = custom_property_dict[custom_property_key]

                    order.custom_properties[custom_property_key] = custom_property

                order.order_items = []
                for order_item_key in order_item_dict:
                    order_item = MwOrderItem()
                    order_item.part_code = order_item_key[1]
                    order_item.context = order_item_key[2]
                    order_item.line_number = order_item_dict[order_item_key][0]
                    order_item.level = order_item_dict[order_item_key][1]
                    order_item.quantity = order_item_dict[order_item_key][2]

                    order.order_items.append(order_item)
                if len(order.order_items) > 0:
                    order.order_items = self._build_order_item_hierarchy(order.order_items)
                all_orders.append(order)

            return sorted(all_orders, key=lambda _: _.id, reverse=self.last_orders_first)

        return self.execute_with_connection(inner_func, db_name=str(self.pos_id))

    def _build_order_item_hierarchy(self, order_items):
        # type: (List[MwOrderItem]) -> List[MwOrderItem]

        # Encontra todos os item que tem context 1
        context_one_items = filter(lambda x: x.context == "1", order_items)

        # Coloca os items dentro do pai de todos
        for context_one_item in context_one_items:
            for order_item in order_items:
                if order_item.line_number == context_one_item.line_number and order_item.part_code != context_one_item.part_code:
                    context_one_item.sons.append(order_item)
                    order_item.parent = context_one_item

        for item in context_one_items:
            self._build_item_tree(item)

        return sorted(context_one_items, cmp=lambda item1, item2: item1.line_number - item2.line_number)

    def _build_item_tree(self, order_item):
        # type: (MwOrderItem) -> None
        all_sons = []  # type: List[MwOrderItem]
        for son in order_item.sons:
            all_sons.append(son)

        # Adicionamos os filhos diretos do item atual
        current_context = order_item.context + "." + str(order_item.part_code)
        order_item.sons = []
        sons_to_remove = []
        for son in all_sons:
            if son.context == current_context:
                order_item.sons.append(son)
                son.parent = order_item
                sons_to_remove.append(son)

        # Os filhos que adicionamos previamente removemos da lista geral
        for son in sons_to_remove:
            all_sons.remove(son)

        sons_to_remove = []
        for current_son in order_item.sons:
            current_son_context = current_son.context + "." + str(current_son.part_code)
            for son in all_sons:
                if son.context.startswith(current_son_context):
                    current_son.sons.append(son)
                    sons_to_remove.append(son)

        if len(sons_to_remove) != len(all_sons):
            message = "Sons not added to any parent"
            raise InvalidSonException(OrderValidationError.InvalidPartForParentPartCode, message)

        for son in order_item.sons:
            self._build_item_tree(son)
