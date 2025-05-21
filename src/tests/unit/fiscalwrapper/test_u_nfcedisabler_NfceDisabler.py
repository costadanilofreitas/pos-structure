# -*- coding: utf-8 -*-
import unittest
import mock
from requests import exceptions
from xml.etree import cElementTree as eTree
from nfceutil import NfceRequest
from nfcedisabler import NfceDisablerRequestBuilder, NfceDisabler, NfceDisablerResponseParser, NfceDisablerResponse, NfceDisablerResponseParserException, ProcInutNfeSaver, \
    ProcInutNfeBuilder


class NfceDisablerTest(unittest.TestCase):
    def __init__(self, method_name):
        super(NfceDisablerTest, self).__init__(method_name)
        self.nfce_disabler_request_builder = mock.NonCallableMagicMock(spec=NfceDisablerRequestBuilder)
        self.nfce_disabler_request_builder.build_request = mock.Mock()

        self.nfce_disabler_response_parser = self._aNfceDisablerResponseParser().build()

        self.nfce_request = self._aNfceRequest().build()

        self.nfce_url = 'http://sefaz.url.com.br'

        self.proc_inut_nfe_builder = mock.NonCallableMagicMock(spec=ProcInutNfeBuilder)
        self.proc_inut_nfe_saver = mock.NonCallableMagicMock(spec=ProcInutNfeSaver)

        self.nfce_disabler = NfceDisabler(
            self.nfce_disabler_request_builder,
            self.nfce_disabler_response_parser,
            self.nfce_request,
            self.nfce_url,
            self.proc_inut_nfe_builder,
            self.proc_inut_nfe_saver,
            1)

    def test_correctValues_requestBuilderIsCalledWithReceivedOrder(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        self.nfce_disabler.disable_fiscal_number(order)

        self.nfce_disabler_request_builder.build_request.assert_called_once_with(order)


    def test_correctValues_nfceRequestIsCalledWithCorrectXmlAndUrl(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        self.nfce_disabler.disable_fiscal_number(order)

        self.nfce_request.envia_nfce.assert_called_once_with(fake_request_xml, self.nfce_url, soap_action="http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao2/nfeInutilizacaoNF2")

    def test_invalidStatusCodeFromSefaz_ExceptionIsThrown(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        self.nfce_disabler_response_parser = self._aNfceDisablerResponseParser().build()

        self.nfce_request = self._aNfceRequest().with_status_code(500).with_text("text").build()

        self._rebuild_nfce_disabler()

        try:
            self.nfce_disabler.disable_fiscal_number(order)
            self.fail("An exception should be thrown")
        except exceptions.HTTPError as ex:
            self.assertEqual(ex.message, "Invalid response code: 500: text")

    def test_exceptionFromNfceDisablerResponseParser_exceptionIsRisenAgain(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        exception = NfceDisablerResponseParserException("exception")
        self.nfce_disabler_response_parser = self._aNfceDisablerResponseParser().with_exception(exception).build()

        self._rebuild_nfce_disabler()

        try:
            self.nfce_disabler.disable_fiscal_number(order)
            self.fail("An exception should be thrown")
        except NfceDisablerResponseParserException as ex:
            self.assertEqual(ex, exception)

    def test_invalidCStatReturned_exceptionIsRisen(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        self.nfce_disabler_response_parser = self._aNfceDisablerResponseParser().with_c_stat("155").build()

        self._rebuild_nfce_disabler()

        try:
            self.nfce_disabler.disable_fiscal_number(order)
            self.fail("An exception should be thrown")
        except Exception as ex:
            self.assertEqual(ex.message, "Invalid cStat 155")

    def test_noExceptions_BuildProdInutNfeXmlCalled(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        fake_response = "response_text"
        self.nfce_request = self._aNfceRequest().with_text(fake_response).build()

        self._rebuild_nfce_disabler()

        self.nfce_disabler.disable_fiscal_number(order)

        self.proc_inut_nfe_builder.build_proc_inut_nfe_xml.assert_called_with(fake_request_xml, fake_response)

    def test_noExceptions_SaveProcInutNfeXmlCalled(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        xml_to_save = "<xml_to_save></<xml_to_save>"
        self.proc_inut_nfe_builder.build_proc_inut_nfe_xml = mock.Mock(return_value=xml_to_save)

        self._rebuild_nfce_disabler()

        self.nfce_disabler.disable_fiscal_number(order)

        self.proc_inut_nfe_saver.save_proc_inut_nfe_xml.assert_called_with(xml_to_save, order)

    def test_validCStatReturned_correclyReturn(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"
        order = eTree.XML(order_xml)

        fake_request_xml = "<xml></xml>"
        self.nfce_disabler_request_builder.build_request = mock.Mock(return_value=fake_request_xml)

        self._rebuild_nfce_disabler()

        self.nfce_disabler.disable_fiscal_number(order)

    def _aNfceRequest(self):
        return NfceRequestBuilder()

    def _aNfceDisablerResponseParser(self):
        return NfceDisablerResponseParserBuilder()

    def _rebuild_nfce_disabler(self):
        self.nfce_disabler = NfceDisabler(
            self.nfce_disabler_request_builder,
            self.nfce_disabler_response_parser,
            self.nfce_request,
            self.nfce_url,
            self.proc_inut_nfe_builder,
            self.proc_inut_nfe_saver,
            1)


class NfceRequestBuilder():
    def __init__(self):
        self.status_code = 200
        self.text = ""

    def with_status_code(self, status_code):
        self.status_code = status_code
        return self

    def with_text(self, text):
        self.text = text
        return self

    def build(self):
        nfce_request = mock.NonCallableMagicMock(spec=NfceRequest)
        response = mock.NonCallableMock()
        response.status_code = self.status_code
        response.text = self.text
        nfce_request.envia_nfce = mock.Mock(return_value=response)

        return nfce_request


class NfceDisablerResponseParserBuilder():
    def __init__(self):
        self.c_stat = "102"
        self.x_motivo = "motivo"
        self.n_prot = "protocolo"
        self.exception = None

    def with_c_stat(self, c_stat):
        self.c_stat = c_stat
        return self

    def with_x_motivo(self, x_motivo):
        self.x_motivo = x_motivo
        return self

    def with_n_prot(self, n_prot):
        self.n_prot = n_prot
        return self

    def with_exception(self, exception):
        self.exception = exception
        return self

    def build(self):
        nfce_disabler_response_parser = mock.NonCallableMagicMock(spec=NfceDisablerResponseParser)

        if self.exception is None:
            nfce_disabler_response = NfceDisablerResponse(self.c_stat, self.x_motivo, self.n_prot)
            nfce_disabler_response_parser.parse_response = mock.Mock(return_value=nfce_disabler_response)
        else:
            nfce_disabler_response_parser.parse_response = mock.Mock(side_effect=self.exception)


        return nfce_disabler_response_parser