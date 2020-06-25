from _ContextKeys import ContextKeys
from _NfceXmlPartBuilder import NfceXmlPartBuilder
from pos_model import Order
from typing import Dict, Any


class TotalBuilder(NfceXmlPartBuilder):
    def __init__(self, versao_ws):
        # type: (int) -> None
        self.versao_ws = versao_ws

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        # Totais da Venda
        v_prod = context[ContextKeys.total_prod]
        v_desc = float(order.discount_amount or 0)
        v_nf = v_prod - v_desc
        v_tot_trib = context[ContextKeys.total_icms] + \
                     context[ContextKeys.total_pis] + \
                     context[ContextKeys.total_cofins]

        context[ContextKeys.v_nf] = v_prod - v_desc

        xml = "<total>" \
              "<ICMSTot>" \
              "<vBC>{v_bc:.02f}</vBC>" \
              "<vICMS>{v_icms:.02f}</vICMS>" \
              "<vICMSDeson>{v_icms_deson:.02f}</vICMSDeson>".format(v_bc=context[ContextKeys.total_vbc],
                                                                    v_icms=context[ContextKeys.total_icms],
                                                                    v_icms_deson=context.get(ContextKeys.deson, 0))
        if self.versao_ws not in (1, 3):
            #xml += "<vFCPUFDest>{v_fcp_uf_dest:.02f}</vFCPUFDest>" \
            #       "<vFCP>{v_fcp:.02f}</vFCP>".format(v_fcp_uf_dest=0,
            #                                            v_fcp=0)
            xml += "<vFCP>{v_fcp:.02f}</vFCP>".format(v_fcp=0)

        xml += "<vBCST>{v_bcst:.02f}</vBCST>" \
               "<vST>{v_st:.02f}</vST>".format(v_bcst=0,
                                               v_st=0)
        if self.versao_ws not in (1, 3):
            xml += "<vFCPST>{v_fcpst:.02f}</vFCPST>" \
                   "<vFCPSTRet>{v_fcpst_ret:.02f}</vFCPSTRet>".format(v_fcpst=0, v_fcpst_ret=0)
        xml += "<vProd>{v_prod:.02f}</vProd>" \
               "<vFrete>{v_frete:.02f}</vFrete>" \
               "<vSeg>{v_seg:.02f}</vSeg>" \
               "<vDesc>{v_desc:.02f}</vDesc>" \
               "<vII>{v_ii:.02f}</vII>" \
               "<vIPI>{v_ipi:.02f}</vIPI>".format(v_prod=v_prod,
                                                  v_frete=0,
                                                  v_seg=0,
                                                  v_desc=v_desc,
                                                  v_ii=0,
                                                  v_ipi=0)
        if self.versao_ws not in (1, 3):
            xml += "<vIPIDevol>{v_ipi_devolv:.02f}</vIPIDevol>".format(v_ipi_devolv=0)
        xml += "<vPIS>{v_pis:.02f}</vPIS>" \
               "<vCOFINS>{v_cofins:.02f}</vCOFINS>" \
               "<vOutro>{v_outro:.02f}</vOutro>" \
               "<vNF>{v_nf:.02f}</vNF>" \
               "<vTotTrib>{v_tot_trib:.02f}</vTotTrib>" \
               "</ICMSTot>" \
               "</total>".format(v_pis=context[ContextKeys.total_pis],
                                 v_cofins=context[ContextKeys.total_cofins],
                                 v_outro=0,
                                 v_nf=v_nf,
                                 v_tot_trib=v_tot_trib)

        return xml
