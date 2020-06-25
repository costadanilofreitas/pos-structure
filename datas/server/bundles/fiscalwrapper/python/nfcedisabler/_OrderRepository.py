import persistence

from msgbus import MBEasyContext
from pos_model import OrderKey, PosConnection
from _ModuleLogger import logger


class OrderRepository(object):
    def __init__(self, mbcontext, pos_list):
        # type: (MBEasyContext, list) -> None
        self.mbcontext = mbcontext
        self.pos_list = pos_list

    def get_all_orders_to_disable(self):
        all_orders_to_disable = []
        for pos_id in self.pos_list:  # type: PosConnection
            pos_connection = None
            try:
                pos_connection = persistence.Driver().open(self.mbcontext, dbname=str(pos_id))
                orders_to_disable = [(str(pos_id), x.get_entry(0)) for x in pos_connection.select("""select OrderId from Orders where OrderId not in
    (
    select o.OrderId
    from Orders o
    inner join OrderCustomProperties ocp
    on o.OrderId = ocp.OrderId
    where ocp.key = 'ORDER_DISABLED'
    or ocp.key = 'CANCELED_AFTER_PAID'
    )
    and StateId = 4 LIMIT 100""")]

                all_orders_to_disable.extend(orders_to_disable)
            except Exception as _:
                logger.exception("Erro buscando orders para inutilizar")
            finally:
                if pos_connection:
                    pos_connection.close()

        return map(lambda pos_order_tuple: OrderKey(pos_order_tuple[0], pos_order_tuple[1]), all_orders_to_disable)

    def mark_order_disabled(self, pos_id, order_id):
        pos_connection = None
        try:
            pos_connection = persistence.Driver().open(self.mbcontext, dbname=str(pos_id))
            self._insert_order_disabled(pos_connection, order_id, "true")
        except Exception as _:
            logger.exception("Erro marcando order como disabled")
        finally:
            if pos_connection:
                pos_connection.close()

    def mark_order_canceled(self, pos_id, order_id):
        pos_connection = None
        try:
            pos_connection = persistence.Driver().open(self.mbcontext, dbname=str(pos_id))
            self._insert_order_canceled(pos_connection, order_id, "true")
        except Exception as _:
            logger.exception("Erro marcando order como cancelada")
        finally:
            if pos_connection:
                pos_connection.close()

    def mark_order_not_disabled(self, pos_id, order_id):
        pos_connection = None
        try:
            pos_connection = persistence.Driver().open(self.mbcontext, dbname=str(pos_id))
            self._insert_order_disabled(pos_connection, order_id, "false")
        except Exception as _:
            logger.exception("Erro marcando order como 'nao inutilizada'")
        finally:
            if pos_connection:
                pos_connection.close()

    @staticmethod
    def _insert_order_disabled(pos_connection, order_id, value):
        pos_connection.query("""INSERT INTO OrderCustomProperties (OrderId, Key, Value) VALUES ({0:s}, "ORDER_DISABLED", "{1:s}")""".format(order_id, value))

    @staticmethod
    def _insert_order_canceled(pos_connection, order_id, value):
        pos_connection.query("""INSERT INTO OrderCustomProperties (OrderId, Key, Value) VALUES ({0:s}, "CANCELED_AFTER_PAID", "{1:s}")""".format(order_id, value))
