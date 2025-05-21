# -*- coding: utf-8 -*-

import json
import logging
from threading import Thread, Condition
from msgbus import TK_SYS_ACK
from time import sleep

from application.model import DispatchedEvents, BusTokens
from application.util import read_sw_config


class RemoteOrderRuptureUpdater(object):
    def __init__(self, mb_context, menu_builder, rupture_repository, update_interval):
        self.mb_context = mb_context
        self.menu_builder = menu_builder
        self.rupture_repository = rupture_repository
        self.update_interval = update_interval
        self.store_id = read_sw_config(mb_context, "Store.Id") or ""
        self.send_rupture_thread_running = False
        self.logger = logging.getLogger("RuptureUpdaterThread")
        self.event_dispatcher = DispatchedEvents(mb_context)

        self.rupture_clean_time_window = None
        self.rupture_clean_time_window_thread_running = None
        self.rupture_clean_time_window_thread_condition = Condition()
        self.start_rupture_clean_time_window_thread()

        if update_interval > 0:
            self.send_rupture_thread_condition = Condition()
            self.start_send_rupture_thread()

    def start_send_rupture_thread(self):
        rupture_event_thread = Thread(target=self.send_rupture_thread, name="SendRuptureThread")
        rupture_event_thread.daemon = True
        rupture_event_thread.start()

        self.logger.info("Thread started")

    def stop_send_rupture_thread(self):
        self.logger.info("Thread stopped")

        self.send_rupture_thread_running = False
        with self.send_rupture_thread_condition:
            self.send_rupture_thread_condition.notify()

    def wake_up_send_rupture_thread(self):
        self.logger.info("Thread waking up...")

        with self.send_rupture_thread_condition:
            self.send_rupture_thread_condition.notify()

    def send_rupture_thread(self):
        self.send_rupture_thread_running = True

        while self.send_rupture_thread_running:
            self.send_rupture_thread_condition.acquire()
            try:
                self._send_rupture_data()
                self.send_rupture_thread_condition.wait(self.update_interval)
            except Exception as _:
                self.logger.exception('Error processing thread')
            finally:
                self.send_rupture_thread_condition.release()

    def start_rupture_clean_time_window_thread(self):
        thread = Thread(target=self.fetch_rupture_clean_time_window_thread, name="RuptureCleanTimeWindowThread")
        thread.daemon = True
        thread.start()

        self.logger.info("RuptureCleanTimeWindow thread started")

    def stop_rupture_clean_time_window_thread(self):
        self.logger.info("RuptureCleanTimeWindow thread stopped")

        self.rupture_clean_time_window_thread_running = False
        with self.rupture_clean_time_window_thread_condition:
            self.rupture_clean_time_window_thread_condition.notify()

    def wake_up_rupture_clean_time_window_thread(self):
        self.logger.info("RuptureCleanTimeWindow thread waking up...")

        with self.rupture_clean_time_window_thread_condition:
            self.rupture_clean_time_window_thread_condition.notify()

    def fetch_rupture_clean_time_window_thread(self):
        self.rupture_clean_time_window_thread_running = True

        while self.rupture_clean_time_window_thread_running:
            self.rupture_clean_time_window_thread_condition.acquire()
            try:
                self._fetch_rupture_clean_time_window()
                self.rupture_clean_time_window_thread_running = False
            except Exception as _:
                self.logger.exception('Error processing thread')
            finally:
                self.rupture_clean_time_window_thread_condition.release()
                sleep(5)

    def update_disabled_items(self, disabled_items):
        self.menu_builder.cached_menu = None
        self.menu_builder.get_menu_as_json(disabled_items)

    def mark_snapshot_as_confirmed(self, snapshot_id):
        self.rupture_repository.mark_snapshot_as_confirmed(snapshot_id)

    def _get_diff_products_status_rupture(self, old_list, new_list, without_combos=False):
        old_menu = self.menu_builder.get_rupture_menu(old_list, without_combos)
        new_menu = self.menu_builder.get_rupture_menu(new_list, without_combos)

        old_disabled = set(x for x in old_menu if old_menu[x][1] is False)
        new_disabled = set(x for x in new_menu if new_menu[x][1] is False)

        items_to_disable = new_disabled.difference(old_disabled)
        items_to_enable = old_disabled.difference(new_disabled)

        ret = []
        ret.extend({'partcode': x, 'name': new_menu[x][0], 'active': False} for x in items_to_disable)
        ret.extend({'partcode': x, 'name': old_menu[x][0], 'active': True} for x in items_to_enable)
        return ret

    def _get_full_products_status(self, snapshot_id):
        product_list = self.rupture_repository.get_snapshot_data(snapshot_id)
        menu = self.menu_builder.get_rupture_menu(product_list, False)

        ret = []
        ret.extend({'partcode': part_code, 'active': menu[part_code][1]} for part_code in menu)
        return ret

    def _send_rupture_data(self):
        last_ok_snapshot_id = self.rupture_repository.get_last_ok_snapshot_id()
        current_snapshot_id = self.rupture_repository.get_current_snapshot_id()
        if last_ok_snapshot_id == current_snapshot_id:
            return

        json_data = self._get_rupture_json(current_snapshot_id)

        if json_data is not None:
            self.logger.info("Pending rupture found, dispatching event to SAC")
            self.logger.info("SnapshotId: {0} \nStoreId: {1} \nData: {2}"
                             .format(current_snapshot_id, self.store_id, json_data))
            self.event_dispatcher.send_event(DispatchedEvents.PosRupture, self.store_id, json_data, logger=self.logger)

    def _build_rupture_json_data(self, product_list, snapshot_id, is_full):
        data = None
        if len(product_list) > 0:
            data = json.dumps(
                {'data': product_list,
                 'full': bool(is_full),
                 'snapshot': str(snapshot_id),
                 'merchantId': str(self.store_id),
                 'ruptureCleanTime': self.rupture_clean_time_window.get("start")
                 })

        return data

    def _fetch_rupture_clean_time_window(self):
        while self.rupture_clean_time_window is None:
            message = self.mb_context.MB_EasySendMessage("Ruptura", BusTokens.TK_RUPTURA_GET_CLEAN_TIME_WINDOW)
            if message.token == TK_SYS_ACK:
                self.rupture_clean_time_window = json.loads(message.data)

    def _get_rupture_json(self, current_snapshot):
        product_list = self._get_full_products_status(current_snapshot)
        json_data = self._build_rupture_json_data(product_list, current_snapshot, True)

        return json_data

    def check_rupture_diff_json(self, current_list, new_list):
        return self._get_diff_products_status_rupture(current_list, new_list, without_combos=True)
