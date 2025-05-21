# -*- coding: utf-8 -*-

from application.customexception import OrderError
from application.model import DispatchedEvents
from application.repository import OrderRepository, ApiOrderRepository
from application.services import logger, ProductionTimeManager, RemoteOrderParser
from msgbus import MBEasyContext


class RemoteOrderPickupTimeUpdater(object):
    OrderJsonTemplate = u"""{{"id":"{0}"}}"""

    def __init__(self, mbcontext, pos_id, order_repository, api_order_repository, remote_order_parser, production_time_manager):
        # type: (MBEasyContext, int, OrderRepository, ApiOrderRepository, RemoteOrderParser, ProductionTimeManager) -> None
        self.mbcontext = mbcontext
        self.pos_id = pos_id
        self.event_dispatcher = DispatchedEvents(mbcontext)
        self.order_repository = order_repository
        self.api_order_repository = api_order_repository
        self.remote_order_parser = remote_order_parser
        self.production_time_manager = production_time_manager

    def update_pickup_time(self):
        orders_to_update = self.order_repository.get_orders_to_update_pickup_time(self.pos_id)
        logger.info("Encontrado {0} orders para atualizar".format(len(orders_to_update)))

        for order in orders_to_update:
            logger.info("Tratando order: {0}".format(order.id))
            if self.production_time_manager.check_time_and_send_to_production(order):
                logger.info(u"Order na hora de ir para produção.")
            else:
                logger.info(u"Order não está na hora de ir para produção. Solicitando atualização de tempo.")
                data = self.OrderJsonTemplate.format(order.id).encode("utf-8")
                self.event_dispatcher.send_event(DispatchedEvents.PosUpdatePickupTime, "", data)

    def pickup_time_updated(self, remote_order_json):
        # type: (unicode) -> None
        pickup_remote_order = self.remote_order_parser.parse_pickup_order(remote_order_json)

        if pickup_remote_order.pickup.time is None:
            return

        if self.api_order_repository.is_order_produced(remote_order_id=pickup_remote_order.id):
            logger.debug(u"Order ja paga. Não vamos atualizar mais.")
            return

        remote_order = self.order_repository.get_single_order_to_update_pickup_time(self.pos_id, pickup_remote_order.id)
        if remote_order is None:
            raise OrderError(pickup_remote_order.id, 4, "No order found with the id: {0}".format(pickup_remote_order.id))

        logger.debug(u"Atualizando tempo da order {0} para {1}".format(remote_order.id, pickup_remote_order.pickup.time.strftime("%Y-%m-%d %H:%M:%S")))

        self.order_repository.update_pickup_time(self.pos_id, remote_order.custom_properties["local_order_id"].value, pickup_remote_order.pickup.time)
        remote_order.pickup.time = pickup_remote_order.pickup.time

        self.production_time_manager.check_time_and_send_to_production(remote_order)
