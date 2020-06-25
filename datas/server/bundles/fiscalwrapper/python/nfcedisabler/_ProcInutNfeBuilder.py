# -*- coding: utf-8 -*-

class ProcInutNfeBuilder(object):
    def __init__(self):
        pass

    @staticmethod
    def build_proc_inut_nfe_xml(request, response, versao_ws):
        # type: (str, str, int) -> str
        index = request.index("<inutNFe ")
        index2 = request.index("</inutNFe>")
        inut_nfe = request[index:index2 + 10]

        index = response.index("<retInutNFe ")
        index2 = response.index("</retInutNFe>")
        ret_inut_nfe = response[index:index2 + 13]

        proc_inut_nfe = "<ProcInutNFe  xmlns=\"http://www.portalfiscal.inf.br/nfe\" versao=\"%.2f\">" % (3.1 if versao_ws in (1, 3) else 4)
        proc_inut_nfe += inut_nfe + ret_inut_nfe
        proc_inut_nfe += "</ProcInutNFe>"

        return proc_inut_nfe.encode("utf8")
