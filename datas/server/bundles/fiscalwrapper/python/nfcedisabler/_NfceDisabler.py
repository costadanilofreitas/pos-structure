# -*- coding: utf-8 -*-
from _NfceDisablerResponseParser import NfceDisablerResponseParser
from _NfceDisablerResponseException import NfceDisablerResponseException
from _NfceDisablerRequestBuilder import NfceDisablerRequestBuilder
from _NfceDisablerResponse import NfceDisablerResponse
from _ProcInutNfeBuilder import ProcInutNfeBuilder
from _ProcInutNfeSaver import ProcInutNfeSaver
from nfcebuilder.nfceutil import NfceRequest
from requests import exceptions


class NfceDisabler(object):
    def __init__(self,
                 nfce_disabler_request_builder,
                 nfce_disabler_response_parser,
                 nfce_request, url_inutilizacao,
                 proc_inut_nfe_builder, 
                 proc_inut_nfe_saver,
                 versao_ws):
        # type: (NfceDisablerRequestBuilder, NfceDisablerResponseParser, NfceRequest, str, ProcInutNfeBuilder, ProcInutNfeSaver, int) -> None
        self.nfce_disabler_request_builder = nfce_disabler_request_builder
        self.nfce_disabler_response_parser = nfce_disabler_response_parser
        self.nfce_request = nfce_request
        self.url_inutilizacao = url_inutilizacao
        self.proc_inut_nfe_builder = proc_inut_nfe_builder
        self.proc_inut_nfe_saver = proc_inut_nfe_saver
        self.versao_ws = versao_ws

        if versao_ws == 1:
            self.soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao2/nfeInutilizacaoNF2"
        elif versao_ws == 3:
            self.soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeInutilizacao3/nfeInutilizacaoNF3"
        else:
            self.soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeInutilizacao4/nfeInutilizacaoNF4"

    def disable_fiscal_number(self, order):
        disable_request_xml = self.nfce_disabler_request_builder.build_request(order)

        response = self.nfce_request.envia_nfce(disable_request_xml, self.url_inutilizacao, soap_action=self.soap_act)
        if response.status_code != 200:
            raise exceptions.HTTPError("Invalid response code: {0}: {1}".format(response.status_code, response.text))

        nfce_disable_response = self.nfce_disabler_response_parser.parse_response(response.text)
        xml = self.proc_inut_nfe_builder.build_proc_inut_nfe_xml(disable_request_xml, response.text, self.versao_ws)

        if nfce_disable_response.c_stat not in (
                NfceDisablerResponse.Disabled,
                NfceDisablerResponse.AlreadyDisabled,
                NfceDisablerResponse.EqualRequest,
                NfceDisablerResponse.OneOfTheRangeAlreadyDisabled):
            self.proc_inut_nfe_saver.save_proc_inut_nfe_xml_error(xml, order)
            raise Exception('Invalid cStat {0}'.format(nfce_disable_response.c_stat))

        self.proc_inut_nfe_saver.save_proc_inut_nfe_xml(xml, order)
