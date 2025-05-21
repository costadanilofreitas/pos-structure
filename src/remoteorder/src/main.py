import os

import cfgtools
from RemoteOrderEventHandler import RemoteOrderEventHandler
from application.compositiontree import CompositionTreeBuilder, DbProductRepository
from application.manager._DeliveryEventsManager import DeliveryEventsManager
from application.model import MessageHandler, ListenedEvents
from application.repository import FiscalRepository, OrderRepository, PriceRepository, ApiOrderRepository, \
    ProductRepository, StoreRepository, CanceledOrderRepository, RuptureRepository, ProducedOrderRepository, \
    LogisticRepository, DeliveryEventsRepository
from application.servicehandlers import LogisticService
from application.services import RemoteOrderProcessor, RemoteOrderParser, RemoteOrderValidator, \
    CompositionTreeValidator, DefaultQuantityFixer, PosStateFixer, MenuBuilder, \
    RemoteOrderRuptureUpdater, ProcessedOrderBuilder, WarningEmitter, StoreService, \
    RemoteOrderTaker, OrderTakerWrapper, RemoteOrderItemCreator, PriceService, RemoteOrderPickupTimeUpdater, \
    ProductionTimeManager, OrderService, ItemsCreator, OrderPriceCalculator, StoreStatusManager
from application.util import read_sw_config
from helper import import_pydevd, config_logger
from application.manager import ProducedOrderManager
from msgbus import MBEasyContext

LOADER_CFG = os.environ["LOADERCFG"]
SERVICE_NAME = "RemoteOrder"


def main():
    import_pydevd(LOADER_CFG, 9139)

    required_services = "Persistence|DeliveryPersistence|StoreWideConfig"

    config_logger(LOADER_CFG, SERVICE_NAME)
    config_logger(LOADER_CFG, "RuptureUpdaterThread", max_files=1)
    config_logger(LOADER_CFG, "ProducedOrdersThread", max_files=1)
    config_logger(LOADER_CFG, "CanceledOrdersThread", max_files=1)
    config_logger(LOADER_CFG, "StoreServiceThread", max_files=1)
    config_logger(LOADER_CFG, "StoreStatusThread", max_files=1)
    config_logger(LOADER_CFG, "LogisticsThreads", max_files=1)

    mb_context = MBEasyContext(SERVICE_NAME)

    config = cfgtools.read(LOADER_CFG)
    pos_id = int(config.find_value("RemoteOrder.PosId"))
    time_to_production_in_minutes = int(config.find_value("RemoteOrder.TimeToProduction"))
    store_status_retry_sync_time = int(config.find_value("RemoteOrder.StoreStatusSyncTime"))
    delivery_user_id = config.find_value("RemoteOrder.DeliveryUserId")
    delivery_password = config.find_value("RemoteOrder.DeliveryPassword")
    price_list_order = config.find_values("RemoteOrder.DeliveryPriceListOrder")
    validate_delivery_price = (config.find_value("RemoteOrder.ValidateDeliveryPrice") or "false").lower() == "true"
    validate_delivery_value = float(config.find_value("RemoteOrder.ValidateDeliveryPriceRange") or 0)
    order_error_wait_time = int(config.find_value("RemoteOrder.OrderErrorSyncInterval") or 0)
    events_sync_interval = int(config.find_value("RemoteOrder.EventsSyncInterval") or 1)
    sync_interval = int(config.find_value("RemoteOrder.SyncInterval") or 0)
    cancel_order_on_partner = (config.find_value("RemoteOrder.CancelOrderOnPartner") or "false").lower() == "true"
    last_orders_first = (config.find_value("RemoteOrder.LastOrdersFirst") or "false").lower() == "true"
    printer_max_retries = int(config.find_value("RemoteOrder.PrinterMaxRetries") or 3)
    printer_retry_time = int(config.find_value("RemoteOrder.PrinterRetryTime") or 3)
    store_status_configurations = config.find_group("RemoteOrder.StoreStatusManager")
    auto_produce = (config.find_value("RemoteOrder.AutoProduce") or "false").lower() == "true"
    sell_with_partner_price = (config.find_value("RemoteOrder.SellWithPartnerPrice") or "false").lower() == "true"
    mandatory_logistic_integration_config_ = config.find_value("RemoteOrder.MandatoryLogisticForIntegration") or "false"
    mandatory_logistic_for_integration = mandatory_logistic_integration_config_.lower() == "true"
    mandatory_logistic_production_config = config.find_value("RemoteOrder.MandatoryLogisticForProduction") or "false"
    mandatory_logistic_for_production = mandatory_logistic_production_config.lower() == "true"
    print_delivery_coupon = (config.find_value("RemoteOrder.PrintDeliveryCoupon") or "false").lower() == "true"
    max_time_to_cancel_orders = int(config.find_value("RemoteOrder.MaxTimeToCancelOrders") or 2)
    use_delivery_fee = (config.find_value("RemoteOrder.UseDeliveryFee") or "false").lower() == "true"
    delivery_fee_part_code = config.find_value("RemoteOrder.DeliveryFeePartCode") or "1000000002"

    apply_default_options_on_sale_config = config.find_value("RemoteOrder.ApplyDefaultOptionOnSale") or "false"
    apply_default_options_on_sale = apply_default_options_on_sale_config.lower() == "true"

    message_handler = MessageHandler(mb_context, SERVICE_NAME, SERVICE_NAME, required_services, None)

    print_app_coupon = (read_sw_config(mb_context, "Store.PrintAppCoupon") or "false").lower() == "true"

    store_id = read_sw_config(mb_context, "Store.Id")

    api_product_repository = ProductRepository(mb_context)

    product_repository = DbProductRepository(mb_context)
    remote_order_parser = RemoteOrderParser(api_product_repository, use_delivery_fee)
    composition_tree_builder = CompositionTreeBuilder(product_repository)
    composition_tree_validator = CompositionTreeValidator(product_repository)

    price_repository = PriceRepository(mb_context)
    price_service = PriceService(price_repository, price_list_order)

    order_price_calculator = OrderPriceCalculator(price_service)

    warning_emitter = WarningEmitter(mb_context)
    remote_order_validator = RemoteOrderValidator(composition_tree_builder,
                                                  composition_tree_validator,
                                                  order_price_calculator,
                                                  warning_emitter,
                                                  validate_delivery_price,
                                                  validate_delivery_value)

    fiscal_repository = FiscalRepository(mb_context)

    order_repository = OrderRepository(mb_context)
    api_order_repository = ApiOrderRepository(mb_context, pos_id, last_orders_first, mandatory_logistic_for_integration)
    api_product_repository = ProductRepository(mb_context)

    default_quantity_fixer = DefaultQuantityFixer(order_repository, api_order_repository, product_repository,
                                                  api_product_repository)

    pos_state_fixer = PosStateFixer(mb_context)

    order_taker_wrapper = OrderTakerWrapper(mb_context, fiscal_repository, api_product_repository,
                                            default_quantity_fixer, pos_state_fixer, delivery_user_id,
                                            delivery_password, price_list_order[0], print_app_coupon,
                                            printer_max_retries, printer_retry_time, sell_with_partner_price,
                                            apply_default_options_on_sale)

    order_item_creator = RemoteOrderItemCreator(order_repository, price_service, sell_with_partner_price,
                                                order_taker_wrapper, pos_id)

    remote_order_taker = RemoteOrderTaker(pos_id, order_taker_wrapper, order_item_creator, order_repository,
                                          delivery_fee_part_code)

    store_repository = StoreRepository(mb_context)
    store_service = StoreService(mb_context, store_repository, store_status_retry_sync_time, store_id)

    store_status_manager = StoreStatusManager(mb_context, store_status_configurations, store_repository)
    store_status_manager.start()

    canceled_order_repository = CanceledOrderRepository(mb_context, pos_id, order_error_wait_time,
                                                        cancel_order_on_partner)
    produced_order_repository = ProducedOrderRepository(pos_id, mb_context)
    items_creator = ItemsCreator(api_product_repository, product_repository)
    order_service = OrderService(api_order_repository, items_creator, remote_order_taker, canceled_order_repository,
                                 produced_order_repository)

    processed_order_builder = ProcessedOrderBuilder(api_product_repository, order_service)
    remote_order_processor = RemoteOrderProcessor(remote_order_parser, remote_order_validator, remote_order_taker,
                                                  store_service, processed_order_builder, cancel_order_on_partner)

    ProducedOrderManager(pos_id, mb_context, order_error_wait_time, produced_order_repository, processed_order_builder)

    production_time_manager = ProductionTimeManager(time_to_production_in_minutes, remote_order_taker,
                                                    produced_order_repository, canceled_order_repository)

    remote_order_pickup_time_updater = RemoteOrderPickupTimeUpdater(mb_context, pos_id, order_repository,
                                                                    api_order_repository, remote_order_parser,
                                                                    production_time_manager)

    menu_builder = MenuBuilder(composition_tree_builder, price_service, product_repository)

    rupture_repository = RuptureRepository(mb_context)
    remote_order_rupture_updater = RemoteOrderRuptureUpdater(mb_context, menu_builder, rupture_repository, sync_interval)

    delivery_events_repository = DeliveryEventsRepository(mb_context, pos_id, produced_order_repository)
    DeliveryEventsManager(pos_id, mb_context, events_sync_interval, delivery_events_repository)

    logistic_service = LogisticService(mb_context, pos_id, order_service, store_id, config, delivery_events_repository)
    LogisticRepository(mb_context, pos_id, order_service, remote_order_processor, logistic_service, config)

    event_handler = RemoteOrderEventHandler(pos_id, mb_context, remote_order_processor,
                                            remote_order_pickup_time_updater, order_service, store_service,
                                            menu_builder, remote_order_rupture_updater, delivery_user_id, pos_id,
                                            store_id, cancel_order_on_partner, store_status_manager, auto_produce,
                                            mandatory_logistic_for_integration, mandatory_logistic_for_production,
                                            print_delivery_coupon, canceled_order_repository, max_time_to_cancel_orders,
                                            logistic_service, delivery_fee_part_code, delivery_events_repository,
                                            use_delivery_fee)

    message_handler.set_event_handler(event_handler)
    message_handler.subscribe_non_reentrant_events([ListenedEvents.UpdatePickupTime])
    message_handler.subscribe_reentrant_events(
        [ListenedEvents.LogisticPickupTimeUpdated, ListenedEvents.SacStoreStatusUpdateAck,
         ListenedEvents.SacOrderMonitorRequest, ListenedEvents.SacOrderCancel,
         ListenedEvents.OrderManagerMenuRequest])
    listened_events = [ListenedEvents.LogisticOrderConfirm, ListenedEvents.Ping, ListenedEvents.RupturaDataUpdated,
                       ListenedEvents.PosOrderProducedAck, ListenedEvents.RuptureAck, ListenedEvents.LogisticSearching,
                       ListenedEvents.LogisticFound, ListenedEvents.LogisticNotFound, ListenedEvents.LogisticCanceled,
                       ListenedEvents.PosLogisticConfirmAck, ListenedEvents.LogisticFinished,
                       ListenedEvents.PosOrderConfirmAck, ListenedEvents.KdsOrderProduced,
                       ListenedEvents.PosOrderReadyToDeliveryAck, ListenedEvents.OrderLogisticDispatched,
                       ListenedEvents.OrderLogisticDelivered, ListenedEvents.PosLogisticDispatchedAck,
                       ListenedEvents.PosLogisticDeliveredAck]

    message_handler.subscribe_queue_events(listened_events)

    message_handler.handle_events()
