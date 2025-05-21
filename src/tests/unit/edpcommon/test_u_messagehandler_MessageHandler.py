# encoding: utf-8
import unittest
import mock
import bustoken
import time

from msgbus import TK_CMP_START, TK_CMP_TERM_NOW, TK_SYS_ACK, TK_SYS_NAK, TK_EVT_EVENT
from messagehandler import EventHandler
from msgbusmock import MBMessageBuilder, MBEasyContextBuilder
from threading import Thread

from messagehandler import MessageHandler


class MessageHandler_HandleEventsTest(unittest.TestCase):
    def test_TK_COMP_TER_NOWReceived_LoopIsStoped(self):
        mbcontext = self._aMBContext().with_message_queue([self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()]).build()

        event_handler = self._aEventHandler().build()

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message =  Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(1)

        self.assertFalse(thread_message.is_alive(), "handle_events method should have returned")
        self.assertTrue(message_handler.finished, "MessageHandler should be finished")
        event_handler.terminate_event.assert_called()

    def test_TK_COMP_STARTReceived_ACKIsResponedOnMBContext(self):
        mbcontext = self._aMBContext().with_message_queue([self._aMBMessage().with_token(TK_CMP_START).build(), self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()]).build()

        event_handler = self._aEventHandler().build()

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message = Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(1)

        mbcontext.MB_EasyReplyMessage.assert_called()
        msg = mbcontext.MB_EasyReplyMessage.call_args_list[0][0][0]
        self.assertEqual(msg.token, TK_SYS_ACK, "TK_SYS_ACK should have been received but wasn´t")

    def test_TK_EVT_EVENTWithAllDataReceived_handleEventCalledWithCorrectEvent(self):
        event_message = self._aMBMessage().with_token(TK_EVT_EVENT).with_data("data\00Subject\00Type").build()
        mbcontext = self._aMBContext().with_message_queue([
            event_message,
            self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()
        ]).build()

        event_handler = self._aEventHandler().build()

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message = Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(1)

        event_handler.handle_event.assert_called_with("Subject", "Type", "data", event_message)

    def test_TK_EVT_EVENTWithOnlySubject_handleEventCalledWithCorrectEvent(self):
        event_message = self._aMBMessage().with_token(TK_EVT_EVENT).with_data("\00Subject").build()
        mbcontext = self._aMBContext().with_message_queue([
            event_message,
            self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()
        ]).build()

        event_handler = self._aEventHandler().build()

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message = Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(1)

        event_handler.handle_event.assert_called_with("Subject", None, "", event_message)

    def test_HandledTokenReceived_HandleMessageCalledOnEventHandler(self):
        handled_token = bustoken.create_token(bustoken.MSGPRT_LOW, "10", "1")

        token_message = self._aMBMessage().with_token(handled_token).build()

        mbcontext = self._aMBContext().with_message_queue([
            token_message,
            self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()
        ]).build()

        event_handler = self._aEventHandler().with_handled_tokens([handled_token]).build()

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message = Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(1)

        event_handler.handle_message.assert_called_with(token_message)

    def test_NotHandledTokenReceived_HandleMessageNotCalledAndNackOnMbContext(self):
        handled_token = bustoken.create_token(bustoken.MSGPRT_LOW, "10", "1")

        token_message = self._aMBMessage().build()

        mbcontext = self._aMBContext().with_message_queue([
            token_message,
            self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()
        ]).build()

        event_handler = self._aEventHandler().with_handled_tokens([handled_token]).build()

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message = Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(1)

        event_handler.handle_message.assert_not_called()
        nack_message = mbcontext.MB_EasyReplyMessage.call_args_list[0][0][0]
        self.assertEqual(nack_message.token, TK_SYS_NAK, "TK_SYS_NAK should be replyed on the message bus but wasn´t")

    def test_secondEventReceivedWhileHandlingFirst_secondIsDiscarded(self):
        event_message = self._aMBMessage().with_token(TK_EVT_EVENT).with_data("data\00Subject\00Type").build()
        mbcontext = self._aMBContext().with_message_queue([
            event_message,
            event_message,
            self._aMBMessage().with_token(TK_CMP_TERM_NOW).build()
        ]).build()

        event_handler = self._aEventHandler().build()
        event_handler.handle_event = mock.Mock(side_effect=self._sleepHalfSecond)

        message_handler = MessageHandler(mbcontext, "", "", "", event_handler)

        thread_message = Thread(target=message_handler.handle_events)
        thread_message.start()
        thread_message.join(10)

        event_handler.handle_event.assert_called_once_with("Subject", "Type", "data", event_message)

    def _sleepHalfSecond(self):
        time.sleep(0.5)

    def _aMBMessage(self):
        return MBMessageBuilder()

    def _aEventHandler(self):
        return EventHandlerBuilder()

    def _aMBContext(self):
        return MBEasyContextBuilder()


class EventHandlerBuilder(object):
    def __init__(self):
        self.handled_tokens = []

    def with_handled_tokens(self, handled_tokens):
        self.handled_tokens = handled_tokens

        return self

    def build(self):
        event_handler = mock.NonCallableMock(spec=EventHandler)
        event_handler.get_handled_tokens = mock.Mock(return_value=self.handled_tokens)
        return event_handler