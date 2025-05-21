# -*- coding: utf-8 -*-

import json
import logging
from datetime import datetime
from threading import Condition, Thread
from typing import Dict

from application.model import Store, StoreStatus, DispatchedEvents, RemoteOrderModelJsonEncoder
from application.customexception import ValidationException, StoreClosedException
from application.repository import StoreRepository
from application.util import read_sw_config
from msgbus import MBEasyContext

logger = logging.getLogger("StoreServiceThread")


class StoreService(object):
    def __init__(self, mb_context, store_repository, retry_sync_time, store_id):
        # type: (MBEasyContext, StoreRepository, int, str) -> None
        self.mb_context = mb_context
        self.store_repository = store_repository
        self.retry_sync_time = retry_sync_time
        
        self.store = Store()
        self.store.id = store_id
        self.store.name = read_sw_config(mb_context, "Store.Name") or ""
        
        self.store.status = self.store_repository.get_current_store_status().status
        self.closed_since = None
        
        self.event_dispatcher = DispatchedEvents(mb_context)
        
        self.thread_condition = Condition()
        self.thread_running = True
        self.update_status_thread = Thread(target=self._send_store_status_to_server)
        self.update_status_thread.daemon = True
        self.update_status_thread.start()
    
    def get_store(self):
        # type: () -> Store
        return self.store
    
    def get_store_status(self):
        # type: () -> Dict
        is_opened = self.store.status == StoreStatus.Open
        closed_since = None
        if closed_since:
            closed_since = "{}:{}".format(self.closed_since.hour, self.closed_since.minute)
        
        return dict(isOpened=is_opened, closedSince=closed_since)
    
    def open_store(self, operator):
        # type: (str) -> Store
        logger.info("Opening store by operator: {}".format(operator))
        return self._change_store_status(StoreStatus.Open, operator)
    
    def close_store(self, operator):
        # type: (str) -> Store
        logger.info("Closing store by operator: {}".format(operator))
        self.closed_since = datetime.now()
        return self._change_store_status(StoreStatus.Closed, operator)
    
    def mark_status_sent(self, data):
        store_status_json = json.loads(data, encoding="utf-8")
        if "id" not in store_status_json:
            raise Exception("Data withou id tag")
        
        status_id = int(store_status_json["id"])
        self.store_repository.mark_status_sent(status_id)
    
    def terminate(self):
        with self.thread_condition:
            self.thread_running = False
            self.thread_condition.notify()
    
    def dispatch_store_status_event(self):
        current_store_status = self.store_repository.get_current_store_status()
        data = json.dumps(current_store_status, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
        logger.info("Store is closed exception triggered, dispatching event to SAC")
        logger.info("Data: {}".format(data))
        self.event_dispatcher.send_event(DispatchedEvents.PosStoreStatusUpdate, "", data, logger=logger)
    
    def _change_store_status(self, new_store_status, operator):
        # type: (unicode, str) -> Store
        if self.store.status == new_store_status:
            msg = "Cannot open store because it is already opened"
            logger.error(msg)
            raise ValidationException("StoreAlreadyOpened", msg)
        
        self.store.status = new_store_status
        self.store_repository.add_store_status(new_store_status, operator)
        with self.thread_condition:
            self.thread_condition.notify()
        
        return self.store
    
    def _send_store_status_to_server(self):
        while self.thread_running:
            store_status_history = self.store_repository.get_not_sent_status()
            if store_status_history is not None:
                data = json.dumps(store_status_history, encoding="utf-8", cls=RemoteOrderModelJsonEncoder)
                logger.info("Pending store status found, dispatching event to SAC")
                logger.info("Data: {}".format(data))
                self.event_dispatcher.send_event(DispatchedEvents.PosStoreStatusUpdate, "", data, logger=logger)
            
            with self.thread_condition:
                self.thread_condition.wait(self.retry_sync_time)
                
    def check_store_is_opened(self):
        if self.store.status != "Open":
            raise StoreClosedException()
