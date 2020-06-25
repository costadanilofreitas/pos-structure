# -*- coding: utf-8 -*-

class NfceDisablerParameters(object):
    ModeloNfce = "65"
    AmbienteProducao = 1
    AmbienteHomologacao = 2
    InfInutTemplate = "<infInut Id='ID{id}'><tpAmb>{tpAmb}</tpAmb><xServ>INUTILIZAR</xServ><cUF>{cUF}</cUF><ano>{ano}</ano><CNPJ>{cnpj}</CNPJ>" \
                      "<mod>65</mod><serie>{serie}</serie><nNFIni>{n_nf_inutilizar}</nNFIni><nNFFin>{n_nf_inutilizar}</nNFFin><xJust>{justificativa}</xJust></infInut>"

    def __init__(self, initial_order_id, tp_amb, c_uf, cnpj, serie, justificativa):
        # type: (int, int, int, str, int, str) -> None
        self.initial_order_id = str(initial_order_id)
        self.tp_amb = str(tp_amb)
        self.c_uf = str(c_uf)
        self.cnpj = cnpj
        self.serie = str(serie)
        self.justificativa = justificativa

    def fill_parameters(self, ano_nota, order_id):
        # type: (str, str) -> str
        nota_inutilizar = str(int(order_id) + int(self.initial_order_id))

        inf_inut_id = self.c_uf + ano_nota + self.cnpj + NfceDisablerParameters.ModeloNfce + self.serie.zfill(3) + nota_inutilizar.zfill(9) + nota_inutilizar.zfill(9)

        return NfceDisablerParameters.InfInutTemplate \
            .format(id=inf_inut_id, ano=ano_nota, n_nf_inutilizar=nota_inutilizar, tpAmb=self.tp_amb, cUF=self.c_uf, cnpj=self.cnpj, serie=self.serie, justificativa=self.justificativa)
