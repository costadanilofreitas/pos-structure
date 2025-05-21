# encoding: utf-8
import unittest
import mock

from msgbus import MBEasyContext, MBMessage, TK_EVT_EVENT,  TK_SYS_ACK, TK_SYS_NAK
from eventhandler import FiscalWrapperEventHandler
from bustoken import TK_FISCALWRAPPER_PROCESS_REQUEST, TK_FISCALWRAPPER_SEARCH_REQUEST, TK_FISCALWRAPPER_REPRINT,\
    TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY, TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST
from nfcedisabler import OrderDisabler, OrderRepository
from ctypes import create_string_buffer
from msgbusmock import MBMessageBuilder


class FiscalWrapperEventHandler_HandleMessage_Test(unittest.TestCase):
    def test_handleMessageDisableOrdersMessageReceived_disableAllOrdersCalled(self):
        mbcontext = mock.NonCallableMagicMock(spec=MBEasyContext)

        order_disabler = mock.NonCallableMagicMock(spec=OrderDisabler)
        order_disabler.disable_all_orders = mock.Mock()

        fiscal_wrapper_event_handler = FiscalWrapperEventHandler(mbcontext, None, None, None, order_disabler, None, False)

        fiscal_wrapper_event_handler.handle_event("DisableNfceOrder", "", "", None)

        order_disabler.disable_all_orders.assert_called()

    def test_disableOrdersMessageReceivedInSatStore_NoException(self):
        mbcontext = mock.NonCallableMagicMock(spec=MBEasyContext)
        mbcontext.MB_ReplyMessage = mock.Mock()

        fiscal_wrapper_event_handler = FiscalWrapperEventHandler(mbcontext, None, None, None, None, None, True)

        fiscal_wrapper_event_handler.handle_event("DisableNfceOrder", "", "", None)

    def _aMBMessage(self):
        return MBMessageBuilder()


class FiscalWrapperEventHandler_GetHandlerTokens_Test(unittest.TestCase):
    def test_getHandledTokens_correctTokensReturned(self):

        event_handler = FiscalWrapperEventHandler(None, None, None, None, None, None, True)
        tokens = event_handler.get_handled_tokens()
        self.assertEqual(len(tokens), 6)
        self.assertTrue(TK_FISCALWRAPPER_PROCESS_REQUEST in tokens, "TK_FISCALWRAPPER_PROCESS_REQUEST not in handled tokens")
        self.assertTrue(TK_FISCALWRAPPER_SEARCH_REQUEST in tokens, "TK_FISCALWRAPPER_SEARCH_REQUEST not in handled tokens")
        self.assertTrue(TK_FISCALWRAPPER_REPRINT in tokens, "TK_FISCALWRAPPER_REPRINT not in handled tokens")
        self.assertTrue(TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY in tokens, "TK_FISCALWRAPPER_DISABLE_ORDERS not in handled tokens")
        self.assertTrue(TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST in tokens, "TK_FISCALWRAPPER_DISABLE_ORDERS not in handled tokens")
