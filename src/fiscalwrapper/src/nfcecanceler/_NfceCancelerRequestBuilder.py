# -*- coding: utf-8 -*-

import base64
import time

from nfcebuilder.nfceutil import NfeSigner, XmlEnveloper
from nfcecanceler import NfceCancelerParameters


class NfceCancelerRequestBuilder(object):
    NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"
    NAMESPACE_WEB_SERVICE = "http://www.portalfiscal.inf.br/nfe/wsdl/RecepcaoEvento"
    NAMESPACE_WEB_SERVICE_4 = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRecepcaoEvento4"

    def __init__(self, canceler_parameters, nfce_signer, xml_enveloper):
        # type: (NfceCancelerParameters, NfeSigner, XmlEnveloper) -> None
        self.canceler_parameters = canceler_parameters
        self.nfce_signer = nfce_signer
        self.xml_enveloper = xml_enveloper

    def build_request(self, order_response, justificativa, versao_ws):
        xml_response = base64.b64decode(order_response + "===")

        idx_start = xml_response.find("<chNFe>") + 7
        idx_final = xml_response.find("</chNFe>")
        chave = xml_response[idx_start:idx_final]

        idx_start = xml_response.find("<nProt>") + 7
        idx_final = xml_response.find("</nProt>")
        nprot = xml_response[idx_start:idx_final]

        parameters_xml = self.canceler_parameters.fill_parameters(chave, nprot, justificativa)

        idlote = int(round(time.time() * 1000))
        cancel_pattern = "<envEvento xmlns=\"{0:s}\" versao=\"1.00\"><idLote>%d</idLote>{1:s}</envEvento>" % idlote

        xml = cancel_pattern.format(NfceCancelerRequestBuilder.NAMESPACE_NFE, parameters_xml)

        signed_xml = self.nfce_signer.sign_cancel_xml(xml)

        envelope = self.xml_enveloper.envelop(signed_xml,
                                              NfceCancelerRequestBuilder.NAMESPACE_WEB_SERVICE if versao_ws in (1, 3)
                                              else NfceCancelerRequestBuilder.NAMESPACE_WEB_SERVICE_4, versao_ws)

        return envelope
