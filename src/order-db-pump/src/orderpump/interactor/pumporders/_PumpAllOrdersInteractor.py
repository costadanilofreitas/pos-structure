from logging import Logger

from orderpump.model import OrderWithError
from orderpump.model.exception import OrderNotFound
from orderpump.repository import OrderPumpRepository
from timeutil import Clock
from unitofwork import UnitOfWork

from ._PumpOrderService import PumpOrderService


class PumpAllOrdersInteractor(object):
    def __init__(self, pump_order_service, order_pump_repository, unit_of_work, clock, batch_size, logger):
        # type: (PumpOrderService, OrderPumpRepository, UnitOfWork, Clock, int, Logger) -> None
        self.pump_order_service = pump_order_service
        self.order_pump_repository = order_pump_repository
        self.unit_of_work = unit_of_work
        self.clock = clock
        self.batch_size = batch_size
        self.logger = logger

    def execute(self):
        # type: () -> None
        def handle_batch():
            sent_orders = 0
            order_to_send = self.order_pump_repository.get_last_order_sent() + 1
            while True:
                try:
                    self.pump_order_service.send(order_to_send)
                except OrderNotFound:
                    self.send_orders_with_error()
                    order_to_send = None
                    return True
                except:
                    self.logger.exception("Error processing order: {}".format(order_to_send))
                    self.order_pump_repository.add_to_error(OrderWithError(order_to_send, self.clock))
                finally:
                    if order_to_send is not None:
                        self.order_pump_repository.set_last_order_processed(order_to_send)

                        order_to_send += 1
                        sent_orders += 1

                        if sent_orders >= self.batch_size:
                            return False

        while not self.unit_of_work.with_transaction(handle_batch):
            pass

    def send_orders_with_error(self):
        try:
            for order_with_error in self.order_pump_repository.get_orders_with_error():
                try:
                    self.pump_order_service.send(order_with_error.order_id)
                    self.order_pump_repository.mark_as_sent(order_with_error.order_id)
                except:
                    self.logger.exception("Error sending order: {}".format(order_with_error))
                    order_with_error.update_retry_count()
                    self.order_pump_repository.update_order_with_error(order_with_error)
        except:
            self.logger.exception("Error sending error orders")
