# -*- coding: utf-8 -*-

from xml.etree import cElementTree as eTree

from _ModuleLogger import logger
from nfcedisabler import NfceDisablerResponse


class NfceDisablerResponseParser(object):
    def __init__(self, versao_ws):
        self.namespace_soap = "http://www.w3.org/2003/05/soap-envelope"

        if versao_ws == 1:
            self.namespace_ret_inutilizacao = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao2"
        elif versao_ws == 3:
            self.namespace_ret_inutilizacao = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao3"
        else:
            self.namespace_ret_inutilizacao = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeInutilizacao4"

    NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"
    NAMESPACE_NFE_KEY = "{http://www.portalfiscal.inf.br/nfe}"


    def parse_response(self, response_str):
        # type: (str) -> NfceDisablerResponse
        try:
            response_xml = eTree.XML(response_str.encode("utf8"))
            logger.info(response_str)
            logger.info(self.namespace_ret_inutilizacao)
            c_stat = response_xml.findall('.//{0}{1}'.format(self.NAMESPACE_NFE_KEY, 'cStat'))[0].text
            x_motivo = response_xml.findall('.//{0}{1}'.format(self.NAMESPACE_NFE_KEY, 'xMotivo'))[0].text
            n_prot_node = response_xml.findall('.//{0}{1}'.format(self.NAMESPACE_NFE_KEY, 'nProt'))
            n_prot = None
            if n_prot_node is not None and len(n_prot_node) > 0:
                n_prot = n_prot_node[0].text

            return NfceDisablerResponse(c_stat, x_motivo, n_prot)
        except Exception as ex:
            logger.error("Erro parseando XML de response: {0}".format(repr(ex)))
