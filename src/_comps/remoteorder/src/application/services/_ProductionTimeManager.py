# -*- coding: utf-8 -*-

from datetime import timedelta, datetime

from application.customexception import OrderException, OrderError, PaymentException, FiscalException
from application.model import RemoteOrder
from application.repository import CanceledOrderRepository, ProducedOrderRepository
from application.services import RemoteOrderTaker
from application.util import convert_from_utf_to_localtime
from dateutil import tz


class ProductionTimeManager(object):
    def __init__(self, time_to_production_in_minutes, remote_order_taker, produced_order_repository, canceled_order_repository):
        # type: (int, RemoteOrderTaker, ProducedOrderRepository, CanceledOrderRepository) -> None
        self.time_to_production_in_minutes = time_to_production_in_minutes
        self.remote_order_taker = remote_order_taker
        self.produced_order_repository = produced_order_repository
        self.canceled_order_repository = canceled_order_repository

    def check_time_and_send_to_production(self, remote_order):
        # type: (RemoteOrder) -> bool
        if remote_order.pickup.time is not None:
            send_to_production_time = datetime.today() + timedelta(minutes=self.time_to_production_in_minutes)
            send_to_production_time = send_to_production_time.replace(tzinfo=tz.tzlocal())

            if convert_from_utf_to_localtime(remote_order.pickup.time) <= send_to_production_time:
                try:
                    self.remote_order_taker.finalize_remote_order(remote_order)
                    self.produced_order_repository.add_produced_order(remote_order.order_id)
                except (OrderException, PaymentException, FiscalException) as e:
                    self.canceled_order_repository.add_canceled_order(remote_order.order_id, e.message)
                    raise OrderError(remote_order.order_id, e.error_code, e.message)

                return True
            else:
                return False
        else:
            return False
