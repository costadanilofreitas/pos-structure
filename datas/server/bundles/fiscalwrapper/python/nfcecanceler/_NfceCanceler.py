# -*- coding: utf-8 -*-

import logging
import os

from nfcebuilder.nfceutil import NfceRequest
from nfcecanceler import NfceCancelerResponseParser, NfceCancelerRequestBuilder, NfceCancelerResponse
from requests import exceptions

logger = logging.getLogger("FiscalWrapper")


class NfceCanceler(object):
    def __init__(self, nfce_canceler_request_builder, nfce_canceler_response_parser, nfce_request, url_cancelamento, dir_enviados, versao_ws):
        # type: (NfceCancelerRequestBuilder, NfceCancelerResponseParser, NfceRequest, str, str, int) -> None
        self.nfce_canceler_request_builder = nfce_canceler_request_builder
        self.nfce_canceler_response_parser = nfce_canceler_response_parser
        self.dir_enviados = dir_enviados
        self.nfce_request = nfce_request
        self.url_cancelamento = url_cancelamento
        self.versao_ws = versao_ws
        if versao_ws in (1, 3):
            self.soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/RecepcaoEvento/nfeRecepcaoEvento"
        else:
            self.soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRecepcaoEvento4/nfeRecepcaoEvento"

    def cancel_order(self, order_response, justificativa):
        cancel_request_xml = self.nfce_canceler_request_builder.build_request(order_response, justificativa, self.versao_ws)

        try:
            response = self.nfce_request.envia_nfce(cancel_request_xml, self.url_cancelamento, soap_action=self.soap_act)
            #logger.info("disable_fiscal_number, request: {} response code: {}: text{}".format(cancel_request_xml, response.status_code, response.text))
        except exceptions.RequestException:
            return False, "Problemas de Conexao"
        except Exception as other_e:
            return False, str(other_e)
        else:
            nfce_canceler_response = self.nfce_canceler_response_parser.parse_response(response.text, self.versao_ws)
            if nfce_canceler_response.c_stat not in (NfceCancelerResponse.Canceled, NfceCancelerResponse.AlreadyCanceled):
                return False, 'Invalid cStat {0}'.format(nfce_canceler_response.c_stat)
            else:
                if nfce_canceler_response.c_stat == NfceCancelerResponse.Canceled:
                    idx_start = cancel_request_xml.find("<chNFe>") + 7
                    idx_final = cancel_request_xml.find("</chNFe>")
                    chave = cancel_request_xml[idx_start:idx_final]
                    serie_nota = chave[22:25]
                    numero_nota = chave[25:34]
                    idx_start = cancel_request_xml.find("<dhEvento>") + 10
                    idx_final = cancel_request_xml.find("</dhEvento>")
                    data_emissao = cancel_request_xml[idx_start:idx_final]
                    dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[5:7], data_emissao[8:10])
                    with open(os.path.join(self.dir_enviados, "Enviados", dir_arquivo, "{0}_{1}_nfe_cancelamento.xml".format(serie_nota, numero_nota)), "w+") as nfe_cancel_file:
                        nfe_cancel_file.write(response.text)
                    return True, "Venda cancelada com sucesso"
                elif nfce_canceler_response.c_stat == NfceCancelerResponse.AlreadyCanceled:
                    return True, "Venda já cancelada anteriormente"
                else:
                    return False, "Erro ao tentar cancelar venda"
