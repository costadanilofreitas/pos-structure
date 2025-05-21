# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from application.model import CurrentOrderItem, RemoteOrder, PickUpInfo, CustomProperty
from application.mwmodel import MwOrderItem
from dateutil import tz
from mwhelper import BaseRepository
from msgbus import MBEasyContext
from persistence import Connection
from typing import List, Optional, Union

logger = logging.getLogger("RemoteOrder")


class OrderRepository(BaseRepository):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        super(OrderRepository, self).__init__(mb_context)

    def update_current_order_items(self, pos_id, current_order_items):
        # type: (int, List[CurrentOrderItem]) -> None

        def inner_func(conn):
            for current_order_item in current_order_items:
                ordered_qty = current_order_item.ordered_quantity if current_order_item.ordered_quantity is not None else None
                last_ordered_qty = current_order_item.last_ordered_quantity if current_order_item.last_ordered_quantity is not None else None
                order_id = current_order_item.order_id
                line_number = current_order_item.line_number
                level = current_order_item.level
                item_id = current_order_item.item_id
                part_code = current_order_item.part_code
                included_quantity = current_order_item.included_quantity
                decremented_quantity = current_order_item.decremented_quantity
                price_key = current_order_item.price_key if current_order_item.price_key is not None else None
                discount_amount = current_order_item.discount_amount
                default_qty = current_order_item.default_qty if current_order_item.default_qty is not None else None
                surcharge_amount = current_order_item.surcharge_amount
                only_flag = current_order_item.only_flag
                overwritten_unit_price = current_order_item.overwritten_unit_price if current_order_item.overwritten_unit_price is not None else None

                ordered_qty_query = "'{}'".format(ordered_qty) if ordered_qty is not None else "NULL"
                last_ordered_qty_query = "'{}'".format(last_ordered_qty) if last_ordered_qty is not None else "NULL"
                price_key_query = "'{}'".format(price_key) if price_key else "NULL"
                default_qty_query = "'{}'".format(default_qty) if default_qty is not None else "NULL"
                overwritten_unit_price_query = "'{}'".format(overwritten_unit_price) if overwritten_unit_price is not None else "NULL"
                
                conn.query("""
                INSERT OR REPLACE INTO orderdb.CurrentOrderItem
                (OrderId, LineNumber, ItemId, Level, PartCode, OrderedQty, LastOrderedQty, IncQty, DecQty, PriceKey, DiscountAmount, SurchargeAmount, OnlyFlag, OverwrittenUnitPrice, DefaultQty)
                VALUES('{}', '{}', '{}', '{}', '{}', {}, {}, '{}', '{}', {}, '{}', '{}', '{}', {}, {}
                )
                """.format(order_id, line_number, item_id, level, part_code, ordered_qty_query, last_ordered_qty_query,
                           included_quantity, decremented_quantity, price_key_query, discount_amount, surcharge_amount,
                           only_flag, overwritten_unit_price_query, default_qty_query))

        self.execute_with_transaction(inner_func, db_name=str(pos_id))

    def update_default_quantities(self, pos_id, order_id, mw_order_items):
        # type: (int, int, List[MwOrderItem]) -> None
        def inner_func(conn):
            # type: (Connection) -> None
            query_template = """Update CurrentOrderItem
                                set DefaultQty = '{0}'
                                where OrderId = '{1}'
                                    and LineNumber = '{2}'
                                    and ItemId = '{3}'
                                    and Level = '{4}'
                                    and PartCode = '{5}';"""

            all_queries = ""
            for item in mw_order_items:
                query = query_template.format(item.default_qty, order_id, item.line_number, item.context, item.level, item.part_code)
                all_queries += query

            if all_queries != "":
                conn.query(all_queries)

        self.execute_with_transaction(inner_func, db_name=str(pos_id))

    def get_orders_to_update_pickup_time(self, pos_id):
        # type: (int) -> List[RemoteOrder]
        def inner_func(conn):
            # type: (Connection) -> List[RemoteOrder]
            order_infos = [(x.get_entry(0), x.get_entry(1), x.get_entry(2)) for x in conn.select("""
            select o.OrderId, ocp.Key, ocp.Value
            from Orders o
            inner join OrderCustomProperties ocp
            on o.OrderId = ocp.OrderId
            where o.StateId = 2 and ocp.OrderId in (
            select OrderId from OrderCustomProperties where Key = 'PICKUP_TYPE' and VALUE = 'delivery') and 
            ocp.OrderId in(
            select OrderId from OrderCustomProperties where Key = 'ORDER_TYPE' and VALUE = 'A'
            )""")]

            ret = {}
            for order_info_tuple in order_infos:
                order_id = order_info_tuple[0]

                if order_id in ret:
                    remote_order = ret[order_id]
                else:
                    remote_order = RemoteOrder()
                    custom_property = CustomProperty()
                    custom_property.key = "local_order_id"
                    custom_property.value = order_id
                    remote_order.custom_properties = {"local_order_id": custom_property}
                    remote_order.pickup = PickUpInfo()

                if order_info_tuple[1] == "REMOTE_ORDER_ID":
                    remote_order.id = order_info_tuple[2]
                elif order_info_tuple[1] == "SCHEDULE_TIME":
                    remote_order.pickup.time = datetime.strptime(order_info_tuple[2], "%Y-%m-%d %H:%M:%S")
                    remote_order.pickup.time = remote_order.pickup.time.replace(tzinfo=tz.tzutc())

                ret[order_id] = remote_order

            return list(ret.values())

        return self.execute_with_connection(inner_func, db_name=str(pos_id))

    def get_single_order_to_update_pickup_time(self, pos_id, remote_order_id):
        # type: (int, int) -> Optional[RemoteOrder]
        def inner_func(conn):
            # type: (Connection) -> Optional[RemoteOrder]
            order_infos = [(x.get_entry(0), x.get_entry(1), x.get_entry(2)) for x in conn.select("""
                            select o.OrderId, ocp.Key, ocp.Value
                            from Orders o
                            inner join OrderCustomProperties ocp
                            on o.OrderId = ocp.OrderId
                            where o.StateId = 2 and o.OrderId in (
                            select OrderId from OrderCustomProperties ocp
                            where ocp.Key = 'REMOTE_ORDER_ID' and ocp.Value = '{0}')""".format(remote_order_id))]

            ret = {}
            for order_info_tuple in order_infos:
                local_order_id = order_info_tuple[0]

                if local_order_id in ret:
                    remote_order = ret[local_order_id]
                else:
                    remote_order = RemoteOrder()
                    custom_property = CustomProperty()
                    remote_order.order_id = local_order_id
                    custom_property.key = "local_order_id"
                    custom_property.value = local_order_id
                    remote_order.custom_properties = {"local_order_id": custom_property}
                    remote_order.pickup = PickUpInfo()

                if order_info_tuple[1] == "REMOTE_ORDER_ID":
                    remote_order.id = order_info_tuple[2]
                elif order_info_tuple[1] == "PICKUP_TIME":
                    remote_order.pickup.time = datetime.strptime(order_info_tuple[2], "%Y-%m-%d %H:%M:%S")
                    remote_order.pickup.time = remote_order.pickup.time.replace(tzinfo=tz.tzutc())

                ret[local_order_id] = remote_order

            if len(ret) > 0:
                return list(ret.values())[0]
            else:
                return None

        return self.execute_with_connection(inner_func, db_name=str(pos_id))

    def update_pickup_time(self, pos_id, order_id, new_pickup_time):
        # type: (int, int, datetime) -> None
        def inner_func(conn):
            # type: (Connection) -> None
            orders = [int(x.get_entry(0)) for x in conn.select("select count(1) from OrderCustomProperties where Key = '{0}' and OrderId = {1}".format("SCHEDULE_TIME", order_id))]
            if len(orders) > 0 and orders[0] > 0:
                conn.query("UPDATE OrderCustomProperties set Value = '{0}' WHERE Key = '{1}' and OrderId = {2}".format(new_pickup_time.strftime("%Y-%m-%d %H:%M:%S"), "SCHEDULE_TIME", order_id))
            else:
                conn.query("INSERT OR IGNORE INTO OrderCustomProperties (OrderId, Key, Value) VALUES ({0}, '{1}', '{2}')".format(order_id, "PICKUP_TIME", new_pickup_time.strftime("%Y-%m-%d %H:%M:%S")))

        self.execute_with_connection(inner_func, db_name=str(pos_id))

    def get_local_order_id(self, pos_id, remote_order_id):
        # type: (int, unicode) -> Union[int]
        def inner_func(conn):
            # type: (Connection) -> RemoteOrder
            local_order_id = [x.get_entry(0) for x in conn.select("""select o.OrderId
        from Orders o
        where o.OrderId in (
        select OrderId from OrderCustomProperties ocp
        where ocp.Key = 'REMOTE_ORDER_ID' and ocp.Value = '{0}'
        )""".format(remote_order_id))]

            if len(local_order_id) > 0:
                return local_order_id[0]

        return self.execute_with_connection(inner_func, db_name=str(pos_id))
