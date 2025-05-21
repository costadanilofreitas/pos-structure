# encoding: utf-8
import sys

from typing import Dict, List
from threading import Thread, Condition
from msgbus import \
    MBException, \
    SE_SUCCESS, \
    TK_CMP_TERM_NOW, \
    TK_CMP_START, \
    TK_EVT_EVENT, \
    TK_SYS_NAK, \
    TK_SYS_ACK

from syserrors import SE_MB_ERR
from systools import sys_log_exception, sys_log_error

from messagebus import Event, Message, DataType
from messagehandler import MessageHandlerBuilder
from _MbContextMessageBus import MbContextMessageBus


class MbContextMessageHandler(object):
    def __init__(self, message_bus, service_name, service_type, required_services, event_handler_builder):
        # type: (MbContextMessageBus, str, str, str, MessageHandlerBuilder) -> None
        self.message_bus = message_bus
        self.service_name = service_name
        self.service_type = service_type
        self.required_services = required_services
        self.event_handler_builder = event_handler_builder
        self.reentrant_subjects = {}
        self.non_reentrant_subjects = {}
        self.queue_subjects = {}
        self.sync_subjects = {}
        self.thread_handling_subject = {}
        self.subject_event_queue = {}  # type: Dict[unicode, List[Event]]
        self.subject_queue_thread = {}  # type: Dict[unicode, Thread]
        self.subject_queue_condition = {}  # type: Dict[unicode, Condition]

        self.tokens = {}
        self.finished = False

        try:
            # Se temos um servico, registramos o mesmo
            if self.service_name and self.service_type != "":
                status = self.message_bus.mbcontext.MB_EasyWaitStart("{}:{}"
                                                                     .format(self.service_name, self.service_type),
                                                                     self.required_services)
                if status != SE_SUCCESS:
                    sys_log_error("Terminating component after 'MB_EasyWaitStart'")
                    sys.exit(status)
        except MBException:
            sys_log_exception("Message-bus error while initializing the FiscalWrapper component. Terminating")
            sys.exit(SE_MB_ERR)

    def subscribe_reentrant_events(self, subjects):
        # type: (List[unicode]) -> MbContextMessageHandler
        for subject in subjects:
            self.reentrant_subjects[subject] = subject
            self.message_bus.subscribe(subject)

        return self

    def subscribe_non_reentrant_events(self, subjects):
        # type: (List[unicode]) -> MbContextMessageHandler
        for subject in subjects:
            self.non_reentrant_subjects[subject] = subject
            self.message_bus.subscribe(subject)

        return self

    def subscribe_queue_events(self, subjects):
        # type: (List[unicode]) -> MbContextMessageHandler
        for subject in subjects:
            self.queue_subjects[subject] = subject

            self.subject_event_queue[subject] = []
            self.subject_queue_condition[subject] = Condition()
            subject_queue_thread = Thread(target=self.event_queue_method,
                                          name=str(subject) + " - Event Queue Thread",
                                          args=(subject,))
            subject_queue_thread.daemon = True
            subject_queue_thread.start()
            self.subject_queue_thread[subject] = subject_queue_thread

            self.message_bus.subscribe(subject)

        return self

    def subscribe_sync_events(self, subjects):
        # type: (List[unicode]) -> MbContextMessageHandler
        for subject in subjects:
            self.sync_subjects[subject] = subject
            self.message_bus.subscribe(subject)

        return self

    def handle_events(self):
        self.event_handler_builder.build_singletons()

        while not self.finished:
            msg = self.message_bus.mbcontext.MB_EasyGetMessage()

            # Check for component terminate request
            if (not msg) or (msg.token == TK_CMP_TERM_NOW):
                # Component terminated, warn the handler that we are terminated
                self.event_handler_builder.destroy_singletons()
                # reply the message
                self.message_bus.mbcontext.MB_EasyReplyMessage(msg)
                # Finish the loop and terminate the component
                self.finished = True
                break

            if msg.token == TK_CMP_START:
                msg.token = TK_SYS_ACK
                self.message_bus.mbcontext.MB_EasyReplyMessage(msg)

            elif msg.token == TK_EVT_EVENT:
                params = msg.data.split('\x00')
                data = params[0] if len(params) > 0 else None
                subject = params[1] if len(params) > 1 else None
                evt_type = params[2] if len(params) > 2 else None
                if evt_type == '':
                    evt_type = None
                sync = params[3] == 'true' if len(params) > 3 else False
                source_id = int(params[4]) if len(params) > 4 else None

                event = Event(subject, evt_type, data, source_id, sync)
                event.imp_message = msg

                if subject in self.non_reentrant_subjects and \
                        subject in self.thread_handling_subject and \
                        self.thread_handling_subject[subject].is_alive():
                    # Se o evento é não reentrante e já temos uma thread tratando outra instância do mesmo evento,
                    # respondemos e não criamos outra thread
                    self.message_bus.mbcontext.MB_EasyReplyMessage(msg)
                    continue

                if subject in self.queue_subjects:
                    # Se o evento é do tipo fila, enfileiramos a tupla e deixamos a thread responsável tratá-lo
                    with self.subject_queue_condition[subject]:
                        self.subject_event_queue[subject].append(event)
                        self.subject_queue_condition[subject].notify()

                    self.message_bus.mbcontext.MB_EasyReplyMessage(msg)
                    continue

                handler_thread = Thread(target=self._handle_event, args=(event, ))
                handler_thread.daemon = True

                if subject in self.non_reentrant_subjects:
                    self.thread_handling_subject[subject] = handler_thread

                handler_thread.start()

                # Se o evento for syncrono, deixamos a thread responsável por dar o reply na mensagem
                if subject not in self.sync_subjects:
                    self.message_bus.mbcontext.MB_EasyReplyMessage(msg)
            # Check for a event request
            else:
                # handles the event ...
                data = msg.data
                data_format = msg.format
                if msg.data is None or msg.data == "":
                    data = None
                    data_format = DataType.empty

                message = Message(msg.token, data_format, data)
                message.imp_message = msg
                handler_thread = Thread(target=self._handle_message, args=(message,))
                handler_thread.daemon = True
                handler_thread.start()

    def event_queue_method(self, subject):
        my_condition = self.subject_queue_condition[subject]
        my_queue = self.subject_event_queue[subject]

        while not self.finished:
            while len(my_queue) > 0:
                with my_condition:
                    event = my_queue.pop(0)

                try:
                    self._handle_event(event)
                except:
                    pass

            with my_condition:
                my_condition.wait()

    def _handle_event(self, event):
        # type: (Event) -> None
        event_handler = None
        try:
            event_handler = self.event_handler_builder.build_message_handler()
            event_handler.handle_event(self.message_bus, event)
        finally:
            if event_handler is not None:
                self.event_handler_builder.destroy_message_handler(event_handler)

    def _handle_message(self, message):
        # type: (Message) -> None
        event_handler = None
        try:
            event_handler = self.event_handler_builder.build_message_handler()
            event_handler.handle_message(self.message_bus, message)
        finally:
            if event_handler is not None:
                self.event_handler_builder.destroy_message_handler(event_handler)
