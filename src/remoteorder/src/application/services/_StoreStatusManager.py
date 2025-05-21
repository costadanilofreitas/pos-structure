# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime, timedelta

from typing import Dict

from application.model import BaseThread, DispatchedEvents, StoreAvailableStatus
from application.repository import StoreRepository
from cfgtools import Group
from msgbus import MBEasyContext


class StoreStatusManager(BaseThread):

    def __init__(self, mb_context, configs, store_repository):
        # type: (MBEasyContext, Group, StoreRepository) -> None

        super(StoreStatusManager, self).__init__()

        self.logger = logging.getLogger("StoreStatusThread")
        self.event_dispatcher = DispatchedEvents(mb_context)
        self.store_repository = store_repository

        self.mb_context = mb_context

        self._load_configurations(configs)

        self.store_status = StoreAvailableStatus.offline
        self.number_of_repeated_ping_received = 0
        self.last_ping_guid = None
        self.last_external_contact_timestamp = None

    def _load_configurations(self, configs):
        # type: (Group) -> None

        def _get(config_name):
            if configs:
                return configs.find_value(config_name)

        self.limit_of_time_without_external_contact = int(_get("LimitOfTimeWithoutExternalContact") or 10)
        self.validate_last_contact_timestamp_frequency = int(_get("ValidateLastContactTimestampFrequency") or 5)
        self.limit_of_repeated_ping_guid_received = int(_get("LimitOfRepeatedPingGUIDReceived") or 5)

    def run(self):

        while self.running:
            try:
                if self.store_status == StoreAvailableStatus.offline:
                    continue

                if self.last_external_contact_timestamp is None:
                    self.logger.error("Never received external contact")
                    self._set_store_status(StoreAvailableStatus.offline)
                    continue

                time_limit = _now() - timedelta(minutes=self.limit_of_time_without_external_contact)
                if time_limit > self.last_external_contact_timestamp:
                    self.logger.error("Exceeded time without external contact")
                    self._set_store_status(StoreAvailableStatus.offline)

            finally:
                self.sleep(self.validate_last_contact_timestamp_frequency * 60)

    def get_store_status(self):
        # type: () -> Dict

        is_online = self.store_status == StoreAvailableStatus.online
        last_external_contact = None
        if self.last_external_contact_timestamp:
            last_external_contact = "{}:{}".format(self.last_external_contact_timestamp.hour,
                                                   self.last_external_contact_timestamp.minute)

        return dict(isOnline=is_online, lastExternalContact=last_external_contact)

    def notify_external_contact_received(self):
        # type: () -> None

        self.last_external_contact_timestamp = _now()

        if self.store_status == StoreAvailableStatus.offline:
            self.logger.info("We were notified by an external contact")
            self._set_store_status(StoreAvailableStatus.online)

    def ping_received(self, guid):
        # type: (str) -> None

        try:
            if guid == self.last_ping_guid:
                self.number_of_repeated_ping_received += 1
                self.logger.info("Repeated ping received. GUID: {}. N#: {}"
                                 .format(guid, self.number_of_repeated_ping_received))

                if self.number_of_repeated_ping_received >= self.limit_of_repeated_ping_guid_received:
                    self.logger.error("Number of repeated pings exceeded")
                    self._set_store_status(StoreAvailableStatus.offline)

                return

            self.logger.info("New ping received. GUID: {}".format(guid))

            self.last_ping_guid = guid
            self.number_of_repeated_ping_received = 0

            self.last_external_contact_timestamp = _now()
            if self.store_status == StoreAvailableStatus.offline:
                self._set_store_status(StoreAvailableStatus.online)
        finally:
            self._reply_ping(guid)

    def _reply_ping(self, guid):
        # type: (str) -> None

        self.logger.info("Replying received ping")
        store_status = self.store_repository.get_current_store_status().status
        data = json.dumps({"guid": guid, "status": store_status})
        self.event_dispatcher.send_event(DispatchedEvents.PosPong, data=data, logger=self.logger)

    def _set_store_status(self, status):
        # type: (str) -> None

        self.logger.info("Setting store status to: {}".format(status.upper()))
        self.store_status = status


def _now():
    # type: () -> datetime

    return datetime.now()
