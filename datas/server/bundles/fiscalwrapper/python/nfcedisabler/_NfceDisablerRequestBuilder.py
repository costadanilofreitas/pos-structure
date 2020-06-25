from nfcebuilder.nfceutil import XmlEnveloper, NfeSigner
from nfcedisabler import NfceDisablerParameters


class NfceDisablerRequestBuilder(object):
    NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"

    def __init__(self, disabler_parameters, nfce_signer, xml_enveloper, versao_ws):
        # type: (NfceDisablerParameters, NfeSigner, XmlEnveloper, int) -> None
        self.disabler_parameters = disabler_parameters
        self.nfce_signer = nfce_signer
        self.xml_enveloper = xml_enveloper
        self.versao_ws = versao_ws
        self.soap_action = None

        if versao_ws == 1:
            self.namespace_ret_inutilizacao = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao2"
        elif versao_ws == 3:
            self.namespace_ret_inutilizacao = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao3"
        else:
            self.namespace_ret_inutilizacao = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeInutilizacao4"

    def build_request(self, order):
        ano_nota = order.get("createdAt")[2:4]
        order_id = order.get("orderId")
        parameters_xml = self.disabler_parameters.fill_parameters(ano_nota, order_id)

        inut_pattern = "<inutNFe xmlns=\"{0:s}\" versao=\"{1:.2f}\">{2:s}</inutNFe>"

        xml = inut_pattern.format(self.NAMESPACE_NFE, 3.1 if self.versao_ws in (1, 3) else 4, parameters_xml)

        signed_xml = self.nfce_signer.sign_xml(xml, "infInut", "Id")

        envelope = self.xml_enveloper.envelop(signed_xml, self.namespace_ret_inutilizacao, self.versao_ws)

        return envelope
