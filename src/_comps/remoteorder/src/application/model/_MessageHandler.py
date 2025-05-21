# encoding: utf-8

import sys
from threading import Thread, Condition

from msgbus import MBException, MBEasyContext, SE_SUCCESS, TK_CMP_TERM_NOW, TK_CMP_START, TK_EVT_EVENT, TK_SYS_NAK, \
    TK_SYS_ACK, MBMessage
from syserrors import SE_MB_ERR
from systools import sys_log_exception, sys_log_info
from typing import List, Dict, Optional


class MessageHandler:
    def __init__(self, mbcontext, service_name, service_type, required_services, event_handler=None):
        # type: (MBEasyContext, str, str, str, Optional[EventHandler]) -> None
        self.mbcontext = mbcontext
        self.service_name = service_name
        self.service_type = service_type
        self.required_services = required_services
        self.event_handler = event_handler
        self.reentrant_subjects = {}
        self.sync_subjects = {}
        self.non_reentrant_subjects = {}
        self.queue_subjects = {}
        self.thread_handling_subject = {}
        self.subject_event_queue = {}  # type: Dict[unicode, List[tuple]]
        self.subject_queue_thread = {}  # type: Dict[unicode, Thread]
        self.subject_queue_condition = {}  # type: Dict[unicode, Condition]

        self.tokens = {}
        self.finished = False

        try:
            # Se temos um servico, registramos o mesmo
            if self.service_name and self.service_type != "":
                status = self.mbcontext.MB_EasyWaitStart("%s:%s" % (self.service_name, self.service_type), self.required_services)
                if status != SE_SUCCESS:
                    sys_log_info("Terminating component after 'MB_EasyWaitStart'")
                    sys.exit(status)
        except MBException:
            sys_log_exception("Message-bus error while initializing component. Terminating")
            sys.exit(SE_MB_ERR)

        if self.event_handler:
            self.subscribe_tokens(self.event_handler.get_handled_tokens())

    def set_event_handler(self, event_handler):
        self.event_handler = event_handler
        self.subscribe_tokens(self.event_handler.get_handled_tokens())

    def subscribe_reentrant_events(self, subjects):
        # type: (List[unicode]) -> MessageHandler
        for subject in subjects:
            self.reentrant_subjects[subject] = subject
            self.mbcontext.MB_EasyEvtSubscribe(subject)

        return self

    def subscribe_non_reentrant_events(self, subjects):
        # type: (List[unicode]) -> MessageHandler
        for subject in subjects:
            self.non_reentrant_subjects[subject] = subject
            self.mbcontext.MB_EasyEvtSubscribe(subject)

        return self

    def subscribe_queue_events(self, subjects):
        for subject in subjects:
            self.queue_subjects[subject] = subject

            self.subject_event_queue[subject] = []
            self.subject_queue_condition[subject] = Condition()
            subject_queue_thread = Thread(target=self.event_queue_method, name=subject + " - Event Queue Thread", args=(subject,))
            subject_queue_thread.daemon = True
            subject_queue_thread.start()
            self.subject_queue_thread[subject] = subject_queue_thread

            self.mbcontext.MB_EasyEvtSubscribe(subject)

        return self

    def subscribe_sync_events(self, subjects):
        for subject in subjects:
            self.sync_subjects[subject] = subject
            self.mbcontext.MB_EasyEvtSubscribe(subject)

        return self

    def subscribe_events(self, subjects):
        # type: (List[unicode]) -> MessageHandler
        return self.subscribe_non_reentrant_events(subjects)

    def subscribe_tokens(self, tokens):
        # type: (list) -> MessageHandler
        for token in tokens:
            self.tokens[token] = token

        return self

    def handle_events(self):
        while not self.finished:
            msg = self.mbcontext.MB_EasyGetMessage()

            # Check for component terminate request
            if (not msg) or (msg.token == TK_CMP_TERM_NOW):
                # Component terminated, warn the handler that we are terminated
                self.event_handler.terminate_event()
                # reply the message
                self.mbcontext.MB_EasyReplyMessage(msg)
                # Finish the loop and terminate the component
                self.finished = True
                break

            if msg.token == TK_CMP_START:
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_EasyReplyMessage(msg)

            elif msg.token == TK_EVT_EVENT:
                params = msg.data.split('\x00')
                data = params[0] if len(params) > 0 else None
                subject = params[1] if len(params) > 1 else None
                evt_type = params[2] if len(params) > 2 else None

                if subject in self.non_reentrant_subjects and subject in self.thread_handling_subject and self.thread_handling_subject[subject].is_alive():
                    # Se o evento é não reentrante e já temos uma thread tratando outra instância do mesmo evento, respondemos e não criamos outra thread
                    self.mbcontext.MB_EasyReplyMessage(msg)
                    continue

                if subject in self.queue_subjects:
                    # Se o evento é do tipo fila, enfileiramos a tupla e deixamos a thread responsável tratá-lo
                    event = (subject, evt_type, data, msg)
                    with self.subject_queue_condition[subject]:
                        self.subject_event_queue[subject].append(event)
                        self.subject_queue_condition[subject].notify()

                    self.mbcontext.MB_EasyReplyMessage(msg)
                    continue

                handler_thread = Thread(target=self.event_handler.handle_event, args=(subject, evt_type, data, msg))
                handler_thread.daemon = True

                if subject in self.non_reentrant_subjects:
                    self.thread_handling_subject[subject] = handler_thread

                handler_thread.start()

                # Se o evento for syncrono, deixamos a thread responsável por dar o reply na mensagem
                if subject not in self.sync_subjects:
                    self.mbcontext.MB_EasyReplyMessage(msg)

            # Check for a event request
            elif msg.token in self.tokens:
                # handles the event ...
                handler_thread = Thread(target=self.event_handler.handle_message, args=(msg,))
                handler_thread.daemon = True
                handler_thread.start()
            else:
                # Ignore any unknown message (just reply it with a TK_SYS_NAK)
                msg.token = TK_SYS_NAK
                self.mbcontext.MB_EasyReplyMessage(msg)

    def event_queue_method(self, subject):
        my_condition = self.subject_queue_condition[subject]
        my_queue = self.subject_event_queue[subject]

        while not self.finished:
            while len(my_queue) > 0:
                with my_condition:
                    event = my_queue.pop(0)

                subject = event[0]
                evt_type = event[1]
                data = event[2]
                msg = event[3]
                try:
                    self.event_handler.handle_event(subject, evt_type, data, msg)
                except:
                    pass

            with my_condition:
                my_condition.wait()


class EventHandler(object):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def get_handled_tokens(self):
        raise NotImplementedError()

    def handle_message(self, msg):
        raise NotImplementedError()

    def handle_event(self, subject, evt_type, data, msg):
        # type: (unicode, unicode, str, MBMessage) -> None
        raise NotImplementedError()

    def terminate_event(self):
        raise NotImplemented()
