# -*- coding: utf-8 -*-
import unittest
import mock
from xml.etree import cElementTree as eTree
from nfceutil import XmlEnveloper, NfceSigner
from nfcedisabler import NfceDisablerParameters, NfceDisablerRequestBuilder


class NfceDisablerRequestBuilderTest(unittest.TestCase):
    def test_disablerParametersCorrectlyCalled(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"

        disabler_parameters = mock.NonCallableMagicMock(spec=NfceDisablerParameters)
        disabler_parameters.fill_parameters = mock.Mock()

        nfce_signer = mock.NonCallableMagicMock(spec=NfceSigner)
        fake_xml_just_to_envelop = "<xml></xml>"
        nfce_signer.sign_xml = mock.Mock(return_value=fake_xml_just_to_envelop)

        xml_enveloper = mock.NonCallableMagicMock(spec=XmlEnveloper)

        order = eTree.XML(order_xml)
        NfceDisablerRequestBuilder(disabler_parameters, nfce_signer, xml_enveloper).build_request(order)

        disabler_parameters.fill_parameters.assert_called_once_with("17", "27")

    def test_signXmlCalled(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"

        disabler_parameters = mock.NonCallableMagicMock(spec=NfceDisablerParameters)
        signed_xml = "<parameters></parameters>"
        disabler_parameters.fill_parameters = mock.Mock(return_value=signed_xml)

        nfce_signer = mock.NonCallableMagicMock(spec=NfceSigner)
        signed_xml = "<signed></signed>"
        nfce_signer.sign_xml = mock.Mock(return_value=signed_xml)

        xml_enveloper = mock.NonCallableMagicMock(spec=XmlEnveloper)

        order = eTree.XML(order_xml)
        NfceDisablerRequestBuilder(disabler_parameters, nfce_signer, xml_enveloper).build_request(order)

        nfce_signer.sign_xml.assert_called_once_with('<inutNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="3.10"><parameters></parameters></inutNFe>', 'infInut', 'Id')

    def test_xmlEnveloperCalled(self):
        order_xml = "<Order orderId='27' createdAt='2017-04-05T09:46:17.278'/>"

        disabler_parameters = mock.NonCallableMagicMock(spec=NfceDisablerParameters)

        nfce_signer = mock.NonCallableMagicMock(spec=NfceSigner)
        signed_xml = "<signed></signed>"
        nfce_signer.sign_xml = mock.Mock(return_value=signed_xml)

        xml_enveloper = mock.NonCallableMagicMock(spec=XmlEnveloper)
        xml_enveloper.envelop = mock.Mock()

        order = eTree.XML(order_xml)
        NfceDisablerRequestBuilder(disabler_parameters, nfce_signer, xml_enveloper).build_request(order)

        xml_enveloper.envelop.assert_called_once_with(signed_xml, NfceDisablerRequestBuilder.NAMESPACE_WEB_SERVICE)