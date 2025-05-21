from datetime import datetime
from logging import Logger
from threading import Lock

from messagebus import Event, MessageBus
from typing import Dict, List, Optional

from ._Subscriber import Subscriber
from .._Cleaner import Cleaner
from .._EventPublisher import EventPublisher
from .._SubscribeCreator import SubscriberCreator
from .._Waiter import Waiter
from .._WaiterRetriever import WaiterRetriever


class EventManager(SubscriberCreator, WaiterRetriever, EventPublisher, Cleaner):
    def __init__(self, message_bus, idle_timeout, bump_timeout, logger):
        # type: (MessageBus, float, float, Logger) -> None
        self.message_bus = message_bus
        self.idle_timeout = idle_timeout
        self.bump_timeout = bump_timeout
        self.logger = logger

        self.lock = Lock()
        self.subscribers = {}  # type: Dict[str, List[Subscriber]]
        self.syncs = {}  # type: Dict[str, Subscriber]

    def create_subscriber(self, subject):
        # type: (str) -> int
        must_subscribe = False
        subscriber = Subscriber()
        with self.lock:
            if subject not in self.subscribers:
                must_subscribe = True
                self.subscribers[subject] = []

            self.subscribers[subject].append(subscriber)
            self.syncs[subscriber.sync_id] = subscriber

        if must_subscribe:
            self.message_bus.subscribe(subject)

        return subscriber.sync_id

    def get_waiter(self, sync_id):
        # type: (str) -> Optional[Waiter]
        with self.lock:
            if sync_id not in self.syncs:
                return None

            subscriber = self.syncs[sync_id]
            waiter = subscriber.get_waiter()
            del self.syncs[sync_id]
            self.syncs[waiter.get_sync_id()] = subscriber

        return waiter

    def new_event(self, event):
        # type: (Event) -> None
        with self.lock:
            if event.subject in self.subscribers:
                for subscriber in self.subscribers[event.subject]:
                    subscriber.new_event(event=event)

    def clean_idle_listeners(self):
        # type: () -> None
        try:
            now = datetime.now()
            events_to_remove = {}  # type: Dict[str, List[Subscriber]]
            subscribers_to_bump = {}
            with self.lock:
                self.logger.debug("Locking for Cleaner")
                for subject in self.subscribers:
                    self.logger.debug("Subject {} has {} listeners".format(subject, len(self.subscribers[subject])))
                    for subscriber in self.subscribers[subject]:
                        if self.is_idle(now, self.idle_timeout, subscriber):
                            if subject not in events_to_remove:
                                events_to_remove[subject] = []
                            events_to_remove[subject].append(subscriber)
                        if self.need_bump(now, self.bump_timeout, subscriber):
                            if subject not in subscribers_to_bump:
                                subscribers_to_bump[subject] = []
                            subscribers_to_bump[subject].append(subscriber)

                for subject in events_to_remove:
                    for subscriber in events_to_remove[subject]:
                        self.subscribers[subject].remove(subscriber)
                        del self.syncs[subscriber.sync_id]

                for subject in subscribers_to_bump:
                    for subscriber in subscribers_to_bump[subject]:
                        event_data = "<Event subject=\"{}\" type=\"\"></Event>".format(subject)
                        subscriber.new_event(Event(subject, "", event_data))
            self.logger.debug("Releasing Lock")
        except BaseException as _:  # noqa
            self.logger.exception("Error cleaning idle listeners")

    def is_idle(self, now, timeout, subscriber):
        return subscriber.pending_waiter is None and (now - subscriber.last_seen).total_seconds() > timeout

    def need_bump(self, now, timeout, subscriber):
        return subscriber.pending_waiter is not None and (now - subscriber.last_seen).total_seconds() > timeout
