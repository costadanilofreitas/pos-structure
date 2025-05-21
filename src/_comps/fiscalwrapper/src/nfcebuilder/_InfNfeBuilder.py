# -*- coding: utf-8 -*-

import base64
import hashlib

from typing import List, Dict, Any
from pos_model import Order
from datetime import datetime
from dateutil import tz

from _NfceXmlPartBuilder import NfceXmlPartBuilder
from _ContextKeys import ContextKeys


class InfNfeBuilder(NfceXmlPartBuilder):
    cnf_random = ""
    cdv = ""

    def __init__(self, part_builders, c_uf, cnpf, modelo, serie, versao_ws):
        # type: (List[NfceXmlPartBuilder], unicode, unicode, unicode, int, float) -> None
        self.part_builders = part_builders
        self.c_uf = c_uf
        self.cnpf = cnpf
        self.modelo = modelo
        self.serie = serie
        self.versao_ws = versao_ws

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        inner_xml = ""
        for part_builder in self.part_builders:
            inner_xml += part_builder.build_xml(order, context)

        infnfe_xml = "<infNFe versao=\"%.2f\" Id=\"NFe${CHAVE_NFCE}\">" % (3.1 if self.versao_ws in (1, 3) else 4)
        infnfe_xml += inner_xml
        infnfe_xml += "</infNFe>"

        fiscal_number = context[ContextKeys.fiscal_number]
        emission_type = context[ContextKeys.emission_type]

        nfce_key = self._calculate_chave(order,
                                         infnfe_xml,
                                         fiscal_number,
                                         emission_type,
                                         context)

        context[ContextKeys.nfce_key] = nfce_key

        hash_csrt = self._calculate_hash_csrt(context)

        infnfe_xml = infnfe_xml\
            .replace(u"${CHAVE_NFCE}", nfce_key)\
            .replace(u"${CNF_RANDOM}", context[ContextKeys.random_number])\
            .replace(u"${HASH_CSRT}", hash_csrt)\
            .replace(u"${CDV}", context[ContextKeys.dv])

        return infnfe_xml

    def _calculate_chave(self, order, infnfe_xml, numero_nota, tp_emis, context):
        # type: (Order, unicode, int, int, Dict[unicode, Any]) -> unicode
        data_emissao = self._formata_data(order.states[len(order.states) - 1].timestamp)

        random_number = self._calculate_random_number(infnfe_xml)
        context[ContextKeys.random_number] = random_number

        chave = "{}{}{}{}{}{:>03}{:09}{}{}".format(self.c_uf,
                                                   data_emissao[2:4],
                                                   data_emissao[5:7],
                                                   self.cnpf,
                                                   self.modelo,
                                                   self.serie,
                                                   numero_nota,
                                                   tp_emis,
                                                   random_number)

        dv = self._calcula_dv(chave)

        context[ContextKeys.dv] = dv

        return chave + dv

    @staticmethod
    def _formata_data(data):
        # type: (datetime) -> unicode
        local_zone = tz.tzlocal()
        data = data.replace(tzinfo=local_zone)
        data_str = data.strftime("%Y-%m-%dT%H:%M:%S%z")
        data_str = data_str[:22] + ":" + data_str[22:]
        return data_str

    @staticmethod
    def _calcula_dv(nfe_key):
        # type: (unicode) -> unicode
        weight = 2
        current_sum = 0
        for i in range(len(nfe_key) - 1, -1, -1):
            current_sum += int(nfe_key[i]) * weight
            if weight < 9:
                weight += 1
            else:
                weight = 2
        digit = 11 - (current_sum % 11)
        if digit > 9:
            digit = 0
        return str(digit)

    @staticmethod
    def _calculate_random_number(xml):
        # type: (unicode) -> unicode
        cnf_random_int = int(hashlib.sha256(xml).hexdigest(), 16) % (10 ** 8)
        cnf_random_str = str(cnf_random_int).zfill(8)
        return cnf_random_str

    @staticmethod
    def _calculate_hash_csrt(context):
        # type: (Dict[unicode, Any]) -> unicode
        hash_csrt = ""

        if 'csrt' and 'id_csrt' in context:
            concatened_value = context[ContextKeys.csrt] + context[ContextKeys.nfce_key]
            hash_csrt = base64.b64encode(hashlib.sha1(concatened_value).digest())

        return hash_csrt
