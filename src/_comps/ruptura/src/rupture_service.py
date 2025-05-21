# -*- coding: utf-8 -*-

import json
from datetime import datetime
from logging import Logger

import sysactions
from bustoken import TK_REMOTE_ORDER_CHECK_RUPTURA_DIFF_ITEMS
from msgbus import MBEasyContext, TK_SYS_ACK, FM_PARAM

from rupture_events import RuptureEvents, RuptureEventTypes
from rupture_repository import RuptureRepository
from model import RuptureItem, RuptureProduct


class RuptureService(object):
    def __init__(self, mb_context, logger, rupture_repository, configs):
        # type: (MBEasyContext, Logger, RuptureRepository, Group) -> None
        super(RuptureService, self).__init__()

        sysactions.mbcontext = mb_context
        self.mb_context = mb_context
        self.logger = logger
        self.rupture_repository = rupture_repository
        self._start = configs.find_value("Rupture.CleanRuptureTimeWindow.StartTime", None)
        self._end = configs.find_value("Rupture.CleanRuptureTimeWindow.EndTime", None)
        self._interval = configs.find_value("Rupture.CleanRuptureTimeWindow.Interval", "00:00:30")

    def get_enabled_items(self):
        self.logger.info("[START] Getting enabled items")
        enabled_items = self.rupture_repository.get_enabled_items()
        self.logger.info("[ END ] Getting enabled items")

        return {x.product_code: x.product_name for x in enabled_items}

    def get_enabled_items_list(self):
        self.logger.info("[START] Getting enabled items")
        enabled_items = self.rupture_repository.get_enabled_items()
        self.logger.info("[ END ] Getting enabled items")

        return self.get_rupture_products(enabled_items)

    def get_disabled_items(self):
        self.logger.info("[START] Getting disabled items")
        disabled_items = self.rupture_repository.get_disabled_items()
        self.logger.info("[ END ] Getting disabled items")

        return {x.product_code: x.product_name for x in disabled_items}

    def get_disabled_items_list(self):
        self.logger.info("[START] Getting disabled items")
        disabled_items = self.rupture_repository.get_disabled_items()
        self.logger.info("[ END ] Getting disabled items")

        return self.get_rupture_products(disabled_items)

    def get_rupture_products(self, items):
        # type: (List[RuptureItem]) -> List[RuptureProduct]
        item_list = []
        for item in items:
            product_code = item.product_code
            product_name = item.product_name
            products_composition = [item.product_part_code] if item.product_part_code else []
            ruptured_product = RuptureProduct(product_code, product_name, products_composition)

            if not next((x for x in item_list if x.product_code == product_code), None):
                item_list.append(ruptured_product)
            else:
                for list_item in item_list:
                    if self._must_add_product_composition(list_item, product_code, products_composition):
                        list_item.products_composition.extend(products_composition)
                        break
        return item_list

    @staticmethod
    def _must_add_product_composition(list_item, product_code, products_composition):
        if list_item.product_code != product_code:
            return False

        return products_composition is not None and products_composition not in list_item.products_composition

    def check_items(self, changes_dict, session_id, all_items):
        message = "[START] Checking items in rupture. SessionId #{} - Items: {}"
        self.logger.info(message.format(session_id, changes_dict))

        items_to_disable = changes_dict.get("disabled") or []

        if not items_to_disable:
            self.logger.info("Has no items in rupture")
            return

        disabled_items = [] if all_items == "True" else list(self.get_disabled_items().iterkeys())
        filtered_items = set(map(lambda y: y["product_code"], items_to_disable)).difference(disabled_items)

        data = str(",".join(filtered_items) + "|" + ",".join(""))

        msg = self.mb_context.MB_EasySendMessage(dest_name="RemoteOrder",
                                                 token=TK_REMOTE_ORDER_CHECK_RUPTURA_DIFF_ITEMS,
                                                 format=FM_PARAM,
                                                 data=data,
                                                 timeout=180 * 1000000)
        if msg.token == TK_SYS_ACK:
            self.logger.info("[END] Checking items in rupture")
            return "" if msg.data == "" else msg.data.split(",")

        raise Exception("Cannot obtain remote order rupture diff items. Response: {}".format(msg.data))

    def update_items(self, changes_json, session_id):
        self.logger.info("[START] Updating items")

        changes_dict = json.loads(changes_json)
        items_to_enable = changes_dict.get("enabled", [])
        items_to_disable = changes_dict.get("disabled", [])
        disabled_items = self.get_disabled_items()

        self.rupture_repository.insert_rupture_update(session_id, items_to_disable, items_to_enable, disabled_items)

        event_data = str(datetime.now().date())
        self.rupture_repository.insert_event_state(event_data)

        snapshot_id = self.create_full_snapshot()

        self.logger.info("[END] Updating items")

        return snapshot_id

    def get_clean_time(self):
        return {
            "start": self._start,
            "end": self._end,
            "interval": self._interval
        }

    def create_full_snapshot(self):
        self.logger.info("[START] Creating rupture full snapshot")

        disabled_items = list(self.get_disabled_items().iterkeys())
        self.rupture_repository.mark_pending_ruptures_as_processed()
        snapshot_id = self.rupture_repository.insert_rupture_snapshot(disabled_items)
        self.rupture_repository.insert_rupture_current_state(snapshot_id)

        self._notify_rupture_changed(disabled_items, snapshot_id)

        self.logger.info("[ END ] Creating rupture full snapshot")

        return snapshot_id

    def clean_rupture_items(self, evt_type=None):
        if evt_type and evt_type == RuptureEventTypes.CleanRuptureThread:
            create_new_snapshot = self._clean_rupture_by_event()
            if create_new_snapshot:
                self.create_full_snapshot()
            self.rupture_repository.mark_clean_rupture_event_as_processed()
        elif evt_type and evt_type != RuptureEvents.CleanRupture:
            self._clean_rupture_by_button(evt_type)
            self.create_full_snapshot()
            self.rupture_repository.mark_clean_rupture_event_as_processed()

    def _notify_rupture_changed(self, disabled_items, snapshot_id):
        params = {
            "disabled_items": disabled_items,
            "snapshot_id": snapshot_id
        }
        self.mb_context.MB_EasyEvtSend("RupturaDataUpdated", "", json.dumps(params))
        self.logger.info("[RuptureDataUpdated] notified!")

    def clean_rupture_totem(self):
        try:
            pos_list = sysactions.get_poslist()
            for pos in pos_list:
                sysactions.set_custom(pos, "RUPTURA_ITEMS", "")
        except BaseException as e:
            self.logger.info('[ruptureItems] Exception {}'.format(e))

    def _clean_rupture_by_event(self):
        self.logger.info("[START] Cleaning all rupture products by event")

        need_to_clean_ruptures = self.rupture_repository.check_if_need_to_clean_ruptures()
        if not need_to_clean_ruptures:
            self.logger.info("[END] Cleaning all rupture products by event. No Ruptures to clean!")
            return False

        self.rupture_repository.clean_rupture_items()
        self.clean_rupture_totem()
        self.rupture_repository.mark_clean_rupture_event_as_processed()

        self.logger.info("[END] Cleaning all rupture products by event. Ruptures cleaned!")
        return True

    def _clean_rupture_by_button(self, evt_type):
        self.logger.info("[START] Cleaning all rupture products by button")
        model = sysactions.get_model(evt_type)

        manager_id = sysactions.get_custom(model, "Last Manager ID")
        enable_session_id = "{} / {} / {}".format(manager_id, sysactions.get_operator_session(model), "CLEAN_BUTTON")

        self.rupture_repository.clean_rupture_items_by_btn(enable_session_id)
        self.logger.info("[ END ] Cleaning all rupture products by button")
