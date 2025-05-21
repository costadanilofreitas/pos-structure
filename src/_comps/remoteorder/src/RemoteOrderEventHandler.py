# -*- coding: utf-8 -*-

import json
import logging
import time
import unicodedata
from json import JSONEncoder
from threading import Lock, Thread

from sysactions import get_model

from application.model import DispatchedEvents, RemoteOrderModelJsonEncoder, EventHandler, BusTokens, ListenedEvents, \
    DeliveryIntegrationStatus
from application.apimodel import ApiModelJsonEncoder
from application.customexception import OrderError, ValidationException
from application.services import RemoteOrderProcessor, RemoteOrderPickupTimeUpdater, OrderService, StoreService, \
    MenuBuilder, RemoteOrderRuptureUpdater, Printer
from application.servicehandlers import IntegrationService, ProductionService, CancellationService, LogisticService
from application.services import StoreStatusManager
from msgbus import MBEasyContext, MBMessage, TK_SYS_ACK, TK_SYS_NAK, FM_STRING, FM_PARAM, MBException
from typing import List, Optional, Type, Union

concurrent_events_lock = Lock()
logger = logging.getLogger("RemoteOrder")


class RemoteOrderEventHandler(EventHandler):
    def __init__(self, pos_id, mb_context, remote_order_processor, remote_order_pickup_time_updater, order_service,
                 store_service, menu_builder, rupture_updater, default_user_id, remote_order_pos_id, store_id,
                 cancel_order_on_partner, store_status_manager, auto_produce, mandatory_logistic_for_integration,
                 mandatory_logistic_for_production, print_delivery_coupon, canceled_order_repository,
                 max_time_to_cancel_orders, logistic_service):
        # type: (int, MBEasyContext, RemoteOrderProcessor, RemoteOrderPickupTimeUpdater, OrderService, StoreService, MenuBuilder, RemoteOrderRuptureUpdater, int, int, int, bool, StoreStatusManager, bool, bool, bool) -> None # noqa
        super(RemoteOrderEventHandler, self).__init__(mb_context)

        self.pos_id = pos_id
        self.remote_order_processor = remote_order_processor
        self.remote_order_pickup_time_updater = remote_order_pickup_time_updater
        self.order_service = order_service
        self.store_service = store_service
        self.menu_builder = menu_builder
        self.unavailable_items = []
        self.rupture_updater = rupture_updater
        self.default_user_id = default_user_id
        self.remote_order_pos_id = remote_order_pos_id
        self.store_id = store_id
        self.handled_tokens = {}
        self.handled_events = self.get_handled_events()
        self.store_status_manager = store_status_manager
        self.event_dispatcher = DispatchedEvents(self.mbcontext)
        self.cancel_order_on_partner = cancel_order_on_partner
        self.auto_produce = auto_produce
        self.mandatory_logistic_for_integration = mandatory_logistic_for_integration
        self.mandatory_logistic_for_production = mandatory_logistic_for_production
        self.print_delivery_coupon = print_delivery_coupon
        self.canceled_order_repository = canceled_order_repository
        self.max_time_to_cancel_orders = max_time_to_cancel_orders

        self.model = get_model(remote_order_pos_id)
        self.cancellation_service = self._create_cancellation_service()
        self.integration_service = self._create_integration_service()
        self.production_service = self._create_production_service()

        self.logistic_service = logistic_service
        self.logistic_service.set_concurrent_events_lock(concurrent_events_lock)

        self.ignored_log_bus_tokens = [BusTokens.TK_REMOTE_ORDER_GET_STORE,
                                       BusTokens.TK_REMOTE_ORDER_GET_STORED_ORDERS,
                                       BusTokens.TK_REMOTE_ORDER_GET_CONFIRMED_ORDERS,
                                       BusTokens.TK_REMOTE_ORDER_GET_VOIDED_ORDERS,
                                       BusTokens.TK_REMOTE_ORDER_GET_STORE_STATUS]
        self.ignored_log_subjects = [ListenedEvents.UpdatePickupTime, ListenedEvents.Ping]

        load_unavailable_items_thread = Thread(target=self.load_unavailable_items, name="Initial Rupture Load Thread")
        load_unavailable_items_thread.daemon = True
        load_unavailable_items_thread.start()

    def load_unavailable_items(self):
        unavailable_items = self.get_rupture_unavailable_items()
        self.update_unavailable_items(unavailable_items)

    def _create_cancellation_service(self):
        return CancellationService(self.model,
                                   self.order_service,
                                   self.canceled_order_repository,
                                   self.max_time_to_cancel_orders,
                                   self.event_dispatcher,
                                   concurrent_events_lock,
                                   logger)

    def _create_integration_service(self):
        return IntegrationService(self.model,
                                  self.store_service,
                                  self.remote_order_processor,
                                  self.order_service,
                                  self.cancellation_service,
                                  self.event_dispatcher,
                                  self.cancel_order_on_partner,
                                  self.mandatory_logistic_for_integration,
                                  concurrent_events_lock,
                                  logger)

    def _create_production_service(self):
        return ProductionService(self.pos_id,
                                 self.mbcontext,
                                 self.model,
                                 self.remote_order_pos_id,
                                 self.order_service,
                                 self.cancellation_service,
                                 self.event_dispatcher,
                                 self.mandatory_logistic_for_production,
                                 self.cancel_order_on_partner,
                                 self.print_delivery_coupon,
                                 concurrent_events_lock,
                                 logger)

    def get_handled_tokens(self):
        # type: () -> List[int]

        tokens = vars(BusTokens).iteritems()
        # noinspection PyTypeChecker
        for token in tokens:
            name, value = token
            if name.startswith("TK_REMOTE_ORDER"):
                self.handled_tokens[value] = name

        return self.handled_tokens.keys()

    def get_handled_events(self):
        # type: () -> List[int]

        self.handled_events = []
        events = vars(ListenedEvents).iteritems()
        # noinspection PyTypeChecker
        for event in events:
            name, value = event
            self.handled_events.append(value)

        return self.handled_events

    def update_unavailable_items(self, unavailable_items):
        self.unavailable_items = unavailable_items
        self.menu_builder.unavailable_items = self.unavailable_items
        self.menu_builder.cached_menu = None
        self.menu_builder.get_menu_as_json()

    def get_rupture_unavailable_items(self):
        while True:
            try:
                msg = self.mbcontext.MB_LocateService(self.mbcontext.hv_service, "Ruptura", maxretries=1)
                if msg:
                    msg = self.mbcontext.MB_EasySendMessage('Ruptura', BusTokens.TK_RUPTURA_GET_DISABLED)
                    if msg.token != TK_SYS_ACK:
                        time.sleep(5)
                        continue

                    return json.loads(msg.data)
            except MBException:
                time.sleep(5)

    def handle_message(self, msg):
        # type: (MBMessage) -> None
        received_token = msg.token
        try:
            if msg.token not in self.handled_tokens:
                logger.info("Not handled token received: [{}]".format(received_token))
                return

            if msg.token not in self.ignored_log_bus_tokens:
                logger.info("New message received: [{}] Data: {}".format(self.handled_tokens[received_token], msg.data))

            if msg.token == BusTokens.TK_REMOTE_ORDER_GET_STORED_ORDERS:
                return_paid_orders = msg.data.lower() == "true" if msg.data else False
                orders = self.order_service.get_stored_orders(return_paid_orders)
                orders_json = self._get_encoded_json(orders, cls=ApiModelJsonEncoder)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=orders_json)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_VOIDED_ORDERS:
                orders = self.order_service.get_error_orders()
                orders_json = self._get_encoded_json(orders, cls=ApiModelJsonEncoder)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=orders_json)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_CONFIRMED_ORDERS:
                orders = self.order_service.get_confirmed_orders()
                orders_json = self._get_encoded_json(orders, cls=ApiModelJsonEncoder)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=orders_json)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_POS_ID:
                data = str(self.remote_order_pos_id)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=data)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION:
                self._handle_produce_remote_order(msg)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_CHECK_IF_ORDER_EXISTS:
                self._check_if_order_exists(msg)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_VOID_REMOTE_ORDER:
                try:
                    msg.token = TK_SYS_ACK
                    data = ""
                    remote_order_id = msg.data
                    self.cancellation_service.trigger_manual_cancel_event(remote_order_id)
                except BaseException as ex:
                    msg.token = TK_SYS_NAK
                    data = ex.message
                    raise
                finally:
                    self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=data)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_REPRINT:
                order_id, retransmit_id = msg.data.split('|')

                self.order_service.reprint_delivery_order(order_id)
                logger.info('Mark retransmit as served: OrderId#{}; RetransmitId#{}'.format(order_id, retransmit_id))

                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data="")

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_STORE:
                store = self.store_service.get_store()
                store_json = self._get_encoded_json(store)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=store_json)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_OPEN_STORE:
                try:
                    store = self.store_service.open_store(msg.data or self.default_user_id)
                    store_json = self._get_encoded_json(store)
                    msg.token = TK_SYS_ACK
                    self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=store_json)
                    self.event_dispatcher.send_event(DispatchedEvents.PosStoreOpened)
                except ValidationException:
                    msg.token = BusTokens.TK_REMOTE_STORE_ALREADY_OPEN
                    self.mbcontext.MB_EasyReplyMessage(msg)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_CLOSE_STORE:
                try:
                    store = self.store_service.close_store(msg.data or self.default_user_id)
                    store_json = self._get_encoded_json(store)
                    msg.token = TK_SYS_ACK
                    self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=store_json)
                    self.event_dispatcher.send_event(DispatchedEvents.PosStoreClosed)
                except ValidationException:
                    msg.token = BusTokens.TK_REMOTE_STORE_ALREADY_CLOSED
                    self.mbcontext.MB_EasyReplyMessage(msg)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_CHECK_RUPTURA_DIFF_ITEMS:
                lists = msg.data.split('|')
                current_list = lists[0].split(',')
                new_list = lists[1].split(',')
                items = self.rupture_updater.check_rupture_diff_json(current_list, new_list)
                ret = []
                for item in items:
                    ret.append(item['name'])
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_PARAM, data=",".join(ret))

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_RUPTURED_ITEMS:
                unavailable_products = self.unavailable_items
                if msg.data:
                    unavailable_products = json.loads(msg.data)

                rupture_menu = self.menu_builder.get_rupture_menu(unavailable_products, False)
                unavailable_products = self._get_ruptured_product_codes(rupture_menu)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=json.dumps(unavailable_products))

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_STORE_STATUS:
                response = dict()
                response.update(self.store_status_manager.get_store_status())
                response.update(self.store_service.get_store_status())
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=json.dumps(response))

            elif msg.token == BusTokens.TK_REMOTE_ORDER_REPRINT_DELIVERY:
                data = msg.data.split("\0")
                pos_id = data[0]
                order_id = data[1]
                pos_list = data[2].split(",")
                Printer(self.mbcontext, pos_id, logger, pos_list).print_delivery_report(order_id)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_GET_LOGISTIC_PARTNERS:
                msg.token = TK_SYS_ACK
                logistic_partners_json = json.dumps(self.logistic_service.logistic_partners)
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=logistic_partners_json)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_SEARCH_LOGISTIC:
                data = json.loads(msg.data).split("\0")
                logistic_partner = data[0]
                order_id = data[1]
                self.logistic_service.set_order_to_search_logistic(order_id, logistic_partner)
                if logistic_partner == 'default' and len(data) >= 3:
                    deliveryman_data = data[2]
                    self.logistic_service.set_deliveryman_data(order_id, deliveryman_data)

                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_SEND_ORDER_TO_LOGISTIC:
                data = msg.data.split("\0")
                order_id = data[1]
                self.logistic_service.logistic_send(order_id)

                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_CANCEL_LOGISTIC:
                data = msg.data.split("\0")
                order_id = data[1]
                self.logistic_service.cancel_logistic(order_id)

                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING)

            elif msg.token == BusTokens.TK_REMOTE_ORDER_SAVE_ORDER:
                order_id = msg.data
                self.remote_order_processor.save_order(order_id)
                
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING)
        
        except BaseException as ex:
            logger.exception("Error handling remote order token: [{}]".format(received_token))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=repr(ex))
        finally:
            if received_token not in self.ignored_log_bus_tokens:
                logger.info("Finishing message: [{}]".format(self.handled_tokens[received_token]))

    @staticmethod
    def _get_ruptured_product_codes(rupture_menu):
        filtered_dict = {k: v for k, v in rupture_menu.iteritems() if not v[1]}
        return filtered_dict.keys()

    def handle_event(self, subject, evt_type, data, msg):
        try:
            if subject not in self.handled_events:
                logger.info("Not handled subject received: [{}]".format(subject))
                return

            if subject not in self.ignored_log_subjects:
                logger.info("New event received: [{}] Data: {}".format(subject, data))

            if subject == ListenedEvents.Ping:
                self.store_status_manager.ping_received(data)
            else:
                self.store_status_manager.notify_external_contact_received()

            if subject == ListenedEvents.RupturaDataUpdated:
                params = json.loads(data)
                items_list = params["disabled_items"] if "disabled_items" in params else json.loads(data)
                snapshot_id = params["snapshot_id"] if "snapshot_id" in params else ''

                self.update_unavailable_items(items_list)

                self.mbcontext.MB_EasyEvtSend("RUPTURE_MODIFIED", "", str(snapshot_id))

            elif subject == ListenedEvents.RuptureAck:
                parsed_json = json.loads(data)
                if "snapshot" in parsed_json:
                    snapshot_id = parsed_json["snapshot"]
                    self.rupture_updater.mark_snapshot_as_confirmed(snapshot_id)

            elif subject == ListenedEvents.LogisticOrderConfirm:
                self._handle_order_confirm(data)

            elif subject == ListenedEvents.UpdatePickupTime:
                try:
                    with concurrent_events_lock:
                        self.remote_order_pickup_time_updater.update_pickup_time()
                except OrderError as ex:
                    order_error_json = self._get_encoded_json(ex)
                    self.event_dispatcher.send_event(DispatchedEvents.PosErrorInPickupOrder, "", order_error_json)

                except Exception as ex:
                    order_error_json = self._get_encoded_json(OrderError(None, 99, repr(ex).encode("utf-8")))
                    self.event_dispatcher.send_event(DispatchedEvents.PosErrorInPickupOrder, "", order_error_json)
                    raise

            elif subject == ListenedEvents.LogisticPickupTimeUpdated:
                try:
                    with concurrent_events_lock:
                        self.remote_order_pickup_time_updater.pickup_time_updated(data)
                        self.event_dispatcher.send_event(DispatchedEvents.PosPickupTimeUpdated, "", data)

                except OrderError as ex:
                    order_error_json = self._get_encoded_json(ex)
                    self.event_dispatcher.send_event(DispatchedEvents.PosErrorInPickupOrder, "", order_error_json)

                except BaseException as ex:
                    order_error_json = self._get_encoded_json(OrderError(None, 99, repr(ex).encode("utf-8")))
                    self.event_dispatcher.send_event(DispatchedEvents.PosErrorInPickupOrder, "", order_error_json)
                    raise

            elif subject == ListenedEvents.SacStoreStatusUpdateAck:
                self.store_service.mark_status_sent(data)

            elif subject == ListenedEvents.SacOrderMonitorRequest:
                return_paid_orders = msg.data.lower() == "true" if msg.data else False
                stored_orders = self.order_service.get_stored_orders(return_paid_orders)
                stored_orders_json = self._get_encoded_json(stored_orders, cls=ApiModelJsonEncoder)
                self.event_dispatcher.send_event(DispatchedEvents.PosOrderMonitorResponse, "", stored_orders_json)

            elif subject == ListenedEvents.SacOrderCancel:
                self.cancellation_service.cancel_order(data)

            elif subject == ListenedEvents.OrderManagerMenuRequest:
                menu = self.menu_builder.get_menu_as_json()
                self.event_dispatcher.send_event(DispatchedEvents.PosMenuResponse, "", menu)

            elif subject == ListenedEvents.PosOrderConfirmAck:
                json_data = json.loads(data)
                local_order_id = json_data.get("localOrderId")
                self.order_service.set_order_custom_property(local_order_id,
                                                             "DELIVERY_INTEGRATION_STATUS",
                                                             DeliveryIntegrationStatus.CONFIRMED)

            elif subject == ListenedEvents.PosOrderProducedAck:
                self.order_service.confirm_produced_order(data)

            elif subject == ListenedEvents.LogisticSearching:
                json_data = json.loads(data)
                remote_order_id = json_data.get("orderId")
                logistic_id = json_data.get("logisticId")
                self.logistic_service.set_logistic_searching_status(remote_order_id, logistic_id)

            elif subject == ListenedEvents.LogisticFound:
                json_data = json.loads(data)
                logistic_id = json_data.get("logisticId")
                remote_order_id = json_data.get("orderId")
                adapter_logistic_id = json_data.get("adapterLogisticId")

                self.logistic_service.logistic_found(logistic_id, remote_order_id, adapter_logistic_id, data)

            elif subject == ListenedEvents.PosLogisticConfirmAck:
                json_data = json.loads(data)
                remote_order_id = json_data.get("id")
                self.logistic_service.logistic_confirm(remote_order_id)

            elif subject == ListenedEvents.LogisticNotFound:
                json_data = json.loads(data)
                remote_order_id = json_data.get("orderId")
                self.logistic_service.logistic_not_found(remote_order_id)

            elif subject == ListenedEvents.LogisticCanceled:
                json_data = json.loads(data)
                logistic_id = json_data.get("logisticId")
                self.logistic_service.logistic_canceled(logistic_id)

            elif subject == ListenedEvents.LogisticFinished:
                json_data = json.loads(data)
                logistic_id = json_data.get("logisticId")
                self.logistic_service.logistic_finished(logistic_id, data)

        except BaseException as _:
            logger.exception("Error processing event [{0}]".format(subject))
        finally:
            if subject not in [ListenedEvents.UpdatePickupTime, ListenedEvents.Ping]:
                logger.info("Finishing event: [{}]".format(subject))

    def terminate_event(self):
        self.store_service.terminate()
        self.rupture_updater.stop_send_rupture_thread()

    def _handle_produce_remote_order(self, msg):
        data = None

        try:
            order_id = int(msg.data.decode("utf-8"))
            self.production_service.produce_order(order_id)
            msg.token = TK_SYS_ACK
        except BaseException as ex:
            data = self._format_exception(ex)
            msg.token = TK_SYS_NAK
            raise
        finally:
            self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=data)

    def _handle_order_confirm(self, data):
        order_id = self.integration_service.create_order(data, self.unavailable_items)

        if self.auto_produce:
            self.production_service.auto_produce_order(order_id)

    @staticmethod
    def _get_data_info(data):
        remote_order_id = None
        originator = None
        try:
            parsed_json = json.loads(data)
            if "id" in parsed_json:
                remote_order_id = parsed_json["id"]
            if "custom_params" in parsed_json and "ORIGINATOR" in parsed_json["custom_params"]:
                originator = parsed_json["custom_params"]["ORIGINATOR"]
        except ValueError:
            pass

        return remote_order_id, originator

    def _check_if_order_exists(self, msg):
        data = ""
        try:
            with concurrent_events_lock:
                data = self.remote_order_processor.check_if_order_exists(json.loads(msg.data.decode("utf-8")))
                data = str(data)
            msg.token = TK_SYS_ACK
        except BaseException as ex:
            msg.token = TK_SYS_NAK
            data = self._format_exception(ex)
            raise
        finally:
            self.mbcontext.MB_ReplyMessage(msg, format=FM_STRING, data=data)

    def _format_exception(self, exception):
        exception_type = type(exception).__name__
        message = "{}: {}".format(exception_type, self._remove_accents(exception.message))

        return message

    @staticmethod
    def _get_encoded_json(ex, cls=RemoteOrderModelJsonEncoder):
        # type: (object, Optional[Type[JSONEncoder]]) -> str

        return json.dumps(ex, encoding="utf-8", cls=cls)

    @staticmethod
    def _remove_accents(text):
        # type: (Union[str, unicode]) -> str
        try:
            text = unicode(text, 'utf-8')
        except (TypeError, NameError):
            pass
        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore')
        text = text.decode("utf-8")
        return str(text)
