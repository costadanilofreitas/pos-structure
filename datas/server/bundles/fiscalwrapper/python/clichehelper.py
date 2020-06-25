# -*- coding: utf-8 -*-

from msgbus import MBEasyContext
from old_helper import read_swconfig


class ClicheHelper(object):
    def __init__(self, mb_context, cnpj_contribuinte, insc_estadual):
        # type: (MBEasyContext, str, str) -> None
        self.mb_context = mb_context
        self.cnpj_contribuinte = cnpj_contribuinte
        self.insc_estadual = insc_estadual
        self.cliche = None

    def get_cliche(self):
        if self.cliche is None:
            razao_social = read_swconfig(self.mb_context, "Store.RazaoSocial")
            end_logradouro = read_swconfig(self.mb_context, "Store.EndLogradouro")
            end_numero = read_swconfig(self.mb_context, "Store.EndNumero").strip() or "S/N"
            end_compl = (read_swconfig(self.mb_context, "Store.EndCompl") or "").strip()
            bairro = read_swconfig(self.mb_context, "Store.Bairro")
            municipio = read_swconfig(self.mb_context, "Store.Municipio")
            cep = read_swconfig(self.mb_context, "Store.CEP")
            uf = read_swconfig(self.mb_context, "Store.UF")
            cnpj_contribuinte = self.cnpj_contribuinte
            inscr_estadual = self.insc_estadual
            formatted_ie = "IE: %s" % inscr_estadual
            self.cliche = [
                razao_social,
                "%s, %s %s %s" % (end_logradouro, end_numero, end_compl, bairro),
                "%s, %s %s-%s" % (municipio, uf, cep[:5], cep[5:]),
                "CNPJ: %s.%s.%s/%s-%s %s" % (cnpj_contribuinte[:2],
                                             cnpj_contribuinte[2:5],
                                             cnpj_contribuinte[5:8],
                                             cnpj_contribuinte[8:12],
                                             cnpj_contribuinte[12:],
                                             formatted_ie)
            ]
        return self.cliche
