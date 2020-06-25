# -*- coding: utf-8 -*-

from datetime import datetime

from nfce import NfceRequestBuilder as RequestBuilder


class NfceCancelerParameters(object):
    ModeloNfce = "65"
    AmbienteProducao = 1
    AmbienteHomologacao = 2
    InfEventoTemplate = "<evento versao=\"1.00\"><infEvento Id='ID110111{chave}01'><cOrgao>{cUF}</cOrgao><tpAmb>{tpAmb}</tpAmb><CNPJ>{cnpj}</CNPJ><chNFe>{chave}</chNFe>" \
                      "<dhEvento>{dh}</dhEvento><tpEvento>110111</tpEvento><nSeqEvento>1</nSeqEvento>" \
                      "<verEvento>1.00</verEvento><detEvento versao=\"1.00\"><descEvento>Cancelamento</descEvento>" \
                      "<nProt>{nprot}</nProt><xJust>{justificativa}</xJust></detEvento></infEvento></evento>"

    def __init__(self, tp_amb, c_uf, cnpj):
        # type: (int, int, str) -> None
        self.tp_amb = str(tp_amb)
        self.c_uf = str(c_uf)
        self.cnpj = cnpj

    def fill_parameters(self, chave, nprot, justificativa):
        # type: (str, str, str) -> str

        dh = RequestBuilder.formata_data(datetime.now())
        return NfceCancelerParameters.InfEventoTemplate \
            .format(chave=chave, tpAmb=self.tp_amb, cUF=self.c_uf, cnpj=self.cnpj, justificativa=justificativa, dh=dh, nprot=nprot)
