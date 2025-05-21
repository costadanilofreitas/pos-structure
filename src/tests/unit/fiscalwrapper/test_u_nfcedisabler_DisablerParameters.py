# encoding: utf-8
import unittest
from nfcedisabler import NfceDisablerParameters


class NfceDisablerParametersTest(unittest.TestCase):
    def test_fill_parameters(self):
        ano_nota = "17"
        numero_nota = "10"

        expected_result = "<infInut Id='ID13173534137200016665001000000110000000110'><tpAmb>2</tpAmb><xServ>INUTILIZAR</xServ><cUF>13</cUF><ano>17</ano><CNPJ>35341372000166</CNPJ>" \
               "<mod>65</mod><serie>1</serie><nNFIni>110</nNFIni><nNFFin>110</nNFFin><xJust>justificativa inutilização</xJust></infInut>"

        c_uf_sp = 13
        xml = aNfceDisablerParameters()\
            .with_initial_order_id(100)\
            .with_serie(1)\
            .with_c_uf(c_uf_sp)\
            .with_tp_amb(NfceDisablerParameters.AmbienteHomologacao)\
            .with_cnpj("35341372000166")\
            .with_justificativa("justificativa inutilização")\
            .build()\
            .fill_parameters(ano_nota, numero_nota)

        self.assertEqual(xml, expected_result)


def aNfceDisablerParameters():
    return NfceDisablerParametersBuilder()


class NfceDisablerParametersBuilder(object):
    def __init__(self):
        self.initial_order_id = 0
        self.tp_amb = 0
        self.c_uf = 0
        self.cnpj = ""
        self.serie = 0
        self.justificativa = ""

    def with_initial_order_id(self, initial_order_id):
        # type: (int) -> NfceDisablerParametersBuilder
        self.initial_order_id = initial_order_id
        return self

    def with_tp_amb(self, tp_amb):
        # type: (int) -> NfceDisablerParametersBuilder
        self.tp_amb = tp_amb
        return self

    def with_c_uf(self, c_uf):
        # type: (int) -> NfceDisablerParametersBuilder
        self.c_uf = c_uf
        return self

    def with_cnpj(self, cnpj):
        # type: (str) -> NfceDisablerParametersBuilder
        self.cnpj = cnpj
        return self

    def with_serie(self, serie):
        # type: (int) -> NfceDisablerParametersBuilder
        self.serie = serie
        return self

    def with_justificativa(self, justificativa):
        # type: (str) -> NfceDisablerParametersBuilder
        self.justificativa = justificativa
        return self

    def build(self):
        return NfceDisablerParameters(self.initial_order_id, self.tp_amb, self.c_uf, self.cnpj, self.serie, self.justificativa)