# -*- coding: utf-8 -*-

import logging
from abc import abstractmethod, ABCMeta

from old_helper import round_half_away_from_zero

logger = logging.getLogger("FiscalWrapper")


class TaxBuilder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_icms(self, cst_icms, tax_item, fcp_item, base_reduction, reason, product_code):
        pass

    @abstractmethod
    def calculate_pis(self, cst_pis, tax_item):
        pass

    @abstractmethod
    def calculate_cofins(self, cst_cofins, tax_item):
        pass


class TaxBuilderLucroReal(TaxBuilder):
    def __init__(self):
        super(TaxBuilder, self).__init__()

    ICMS_00 = "<ICMS>" \
                "<ICMS00>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.04f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                  "{fcp_data}" \
                "</ICMS00>" \
              "</ICMS>"
    ICMS_00_FCP = "<pFCP>{p_fcp:.04f}</pFCP>" \
                  "<vFCP>{v_fcp:.02f}</vFCP>"

    ICMS_20 = "<ICMS>" \
                "<ICMS20>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<pRedBC>{p_red_bc:.02f}</pRedBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.04f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                  "{fcp_data}" \
                "</ICMS20>" \
              "</ICMS>"
    ICMS_20_FCP = "<vBCFCP>{bc_fcp:.02f}</vBCFCP>" \
                  "<pFCP>{p_fcp:.04f}</pFCP>" \
                  "<vFCP>{v_fcp:.02f}</vFCP>"

    ICMS_40 = "<ICMS>" \
                "<ICMS40>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "{reason_data}" \
                "</ICMS40>" \
              "</ICMS>"
    ICMS_40_REASON = "<vICMSDeson>{deson:.02f}</vICMSDeson>" \
                     "<motDesICMS>{reason}</motDesICMS>"
    ICMS_60 = "<ICMS>" \
                "<ICMS60>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "{fcp_data}" \
                  "<pRedBCEfet>0.00</pRedBCEfet>" \
                  "<vBCEfet>0.00</vBCEfet>" \
                  "<pICMSEfet>0.0000</pICMSEfet>" \
                  "<vICMSEfet>0.00</vICMSEfet>" \
              "</ICMS60>" \
              "</ICMS>"
    ICMS_60_FCP = "<vBCFCPSTRet>{bc_fcp:.02f}</vBCFCPSTRet>" \
                  "<pFCPSTRet>{p_fcp:.04f}</pFCPSTRet>" \
                  "<vFCPSTRet>{v_fcp:.02f}</vFCPSTRet>"

    ICMS_90 = "<ICMS>" \
                "<ICMS90>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.02f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                  "{fcp_data}" \
                "</ICMS90>" \
              "</ICMS>"
    ICMS_90_FCP = "<vBCFCP>{bc_fcp:.02f}</vBCFCP>" \
                  "<pFCP>{p_fcp:.04f}</pFCP>" \
                  "<vFCP>{v_fcp:.02f}</vFCP>"

    PIS_NT = "<PIS>" \
               "<PISNT>" \
                 "<CST>{cst:>02}</CST>" \
               "</PISNT>" \
             "</PIS>"
    PIS_ALIQ = "<PIS>" \
                 "<PISAliq>" \
                   "<CST>{cst:>02}</CST>" \
                   "<vBC>{v_bc:.02f}</vBC>" \
                   "<pPIS>{p_pis:.04f}</pPIS>" \
                   "<vPIS>{v_pis:0.2f}</vPIS>" \
                 "</PISAliq>" \
               "</PIS>"
    COFINS_NT = "<COFINS>" \
                  "<COFINSNT>" \
                    "<CST>{cst:>02}</CST>" \
                  "</COFINSNT>" \
                "</COFINS>"
    COFINS_ALIQ = "<COFINS>" \
                    "<COFINSAliq>" \
                      "<CST>{cst:>02}</CST>" \
                      "<vBC>{v_bc:.02f}</vBC>" \
                      "<pCOFINS>{p_cofins:.04f}</pCOFINS>" \
                      "<vCOFINS>{v_cofins:0.2f}</vCOFINS>" \
                    "</COFINSAliq>" \
                  "</COFINS>"

    def calculate_icms(self, cst_icms, csosn, tax_item, fcp_item, base_reduction, reason, product_code):
        # returns xml line, base amount, tax amount and deson
        _round_tax_amount(tax_item)
        if cst_icms == 0 and tax_item:
            fcp_data = ""
            fcp_tax = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_00_FCP.format(p_fcp=fcp_item.tax_rate*100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad
            xml = self.ICMS_00.format(orig=0,
                                      cst=cst_icms,
                                      mod_bc=3,
                                      v_bc=tax_item.base_amount_ad,
                                      p_icms=tax_item.tax_rate * 100,
                                      v_icms=tax_item.tax_amount_ad,
                                      fcp_data=fcp_data)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad, 0, fcp_tax, 0, 0

        elif cst_icms == 20 and tax_item:
            fcp_data = ""
            fcp_tax = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_20_FCP.format(bc_fcp=tax_item.base_amount_ad,
                                                   p_fcp=fcp_item.tax_rate * 100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad

            xml = self.ICMS_20.format(orig=0,
                                      cst=cst_icms,
                                      mod_bc=3,
                                      v_bc=tax_item.base_amount_ad,
                                      p_red_bc=base_reduction,
                                      p_icms=tax_item.tax_rate * 100,
                                      v_icms=tax_item.tax_amount_ad,
                                      fcp_data=fcp_data)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad, 0, fcp_tax, 0, 0

        elif cst_icms == 40 and tax_item:
            if tax_item.tax_amount_ad > 0:
                logger.warning("CST ICMS = 40, tax amount maior que zero")
            if not reason:
                logger.warning("CST ICMS = 40, não possui motivo, usando padrão 9")
                reason = "9"
            xml = self.ICMS_40.format(orig=0,
                                      cst=cst_icms,
                                      reason_data=self.ICMS_40_REASON.format(deson=tax_item.tax_amount_ad, reason=reason) if reason else '')
            return xml, 0, 0, tax_item.tax_amount_ad if reason else 0, 0, 0, 0

        elif cst_icms == 60 and tax_item:
            fcp_data = ""
            fcp_tax = 0
            fcp_tax_rate = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_60_FCP.format(bc_fcp=tax_item.base_amount_ad,
                                                   p_fcp=fcp_item.tax_rate * 100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad
                fcp_tax_rate = fcp_item.tax_rate * 100
            if tax_item.tax_amount_ad > 0:
                logger.warning("CST ICMS = 60, tax amount maior que zero")

            xml = self.ICMS_60.format(orig=0, cst=cst_icms, pst=tax_item.tax_rate*100 + fcp_tax_rate, fcp_data=fcp_data)
            return xml, 0, 0, 0, 0, 0, fcp_tax

        elif cst_icms == 90 and tax_item:
            fcp_data = ""
            fcp_tax = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_90_FCP.format(bc_fcp=tax_item.base_amount_ad,
                                                   p_fcp=fcp_item.tax_rate * 100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad

            xml = self.ICMS_90.format(orig=0,
                                      cst=cst_icms,
                                      mod_bc=3,
                                      v_bc=tax_item.base_amount_ad,
                                      p_icms=tax_item.tax_rate * 100,
                                      v_icms=tax_item.tax_amount_ad,
                                      fcp_data=fcp_data)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad, 0, fcp_tax, 0, 0

        else:
            if not tax_item:
                raise Exception("ICMS não encontrado no produto: {}".format(product_code))
            raise Exception("CST ICMS ou taxa não esperado: {}. Produto: {}".format(cst_icms, product_code))

    def calculate_pis(self, cst_pis, tax_item):
        _round_tax_amount(tax_item)
        if cst_pis in (1, 2, 99) and tax_item:
            xml = self.PIS_ALIQ.format(cst=cst_pis,
                                       v_bc=tax_item.base_amount_ad,
                                       p_pis=tax_item.tax_rate * 100,
                                       v_pis=tax_item.tax_amount_ad)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad

        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0

        else:
            raise Exception("CST PIS ou taxa Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        _round_tax_amount(tax_item)
        if cst_cofins in (1, 2, 99) and tax_item:
            xml = self.COFINS_ALIQ.format(cst=cst_cofins,
                                          v_bc=tax_item.base_amount_ad,
                                          p_cofins=tax_item.tax_rate * 100,
                                          v_cofins=tax_item.tax_amount_ad)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad

        elif cst_cofins in (4, 5, 6, 7, 8, 9):
            return self.COFINS_NT.format(cst=cst_cofins), 0, 0

        else:
            raise Exception("CST COFINS ou taxa Não Esperado: %s" % cst_cofins)


class TaxBuilderSimplesNacional(TaxBuilder):
    def __init__(self):
        super(TaxBuilderSimplesNacional, self).__init__()

    ICMSSN_101 = "<ICMS>" \
                   "<ICMSSN101>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN101>" \
                 "</ICMS>"

    ICMSSN_102 = "<ICMS>" \
                   "<ICMSSN102>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN102>" \
                 "</ICMS>"
    
    ICMSSN_201 = "<ICMS>" \
                   "<ICMSSN201>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN201>" \
                 "</ICMS>"
    
    ICMSSN_202 = "<ICMS>" \
                   "<ICMSSN202>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN202>" \
                 "</ICMS>"
    
    ICMSSN_500 = "<ICMS>" \
                   "<ICMSSN500>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                     "{fcp_data}" \
                     "<pRedBCEfet>0.00</pRedBCEfet>" \
                     "<vBCEfet>0.00</vBCEfet>" \
                     "<pICMSEfet>0.0000</pICMSEfet>" \
                     "<vICMSEfet>0.00</vICMSEfet>" \
                 "</ICMSSN500>" \
                 "</ICMS>"
    
    ICMSSN_500_FCP = "<vBCFCPSTRet>{bc_fcp:.02f}</vBCFCPSTRet>" \
                     "<pFCPSTRet>{p_fcp:.04f}</pFCPSTRet>" \
                     "<vFCPSTRet>{v_fcp:.02f}</vFCPSTRet>"

    ICMSSN_900 = "<ICMS>" \
                     "<ICMSSN900>" \
                         "<orig>{orig}</orig>" \
                         "<CSOSN>{csosn}</CSOSN>" \
                     "</ICMSSN900>" \
                 "</ICMS>"

    PIS_OUTR = "<PIS>" \
                 "<PISOutr>" \
                   "<CST>{cst:0>2}</CST>" \
                   "<qBCProd>{q_bc_prod:.02f}</qBCProd>" \
                   "<vAliqProd>{v_aliq_prod:.04f}</vAliqProd>" \
                   "<vPIS>{v_pis:0.2f}</vPIS>" \
                 "</PISOutr>" \
               "</PIS>"
    
    PIS_NT = "<PIS>" \
               "<PISNT>" \
                 "<CST>{cst:>02}</CST>" \
               "</PISNT>" \
             "</PIS>"
    
    COFINS_OUTR = "<COFINS>" \
                    "<COFINSOutr>" \
                      "<CST>{cst:0>2}</CST>" \
                      "<qBCProd>{q_bc_prod:.02f}</qBCProd>" \
                      "<vAliqProd>{v_aliq_prod:.04f}</vAliqProd>" \
                      "<vCOFINS>{v_cofins:0.2f}</vCOFINS>" \
                    "</COFINSOutr>" \
                  "</COFINS>"
    
    COFINS_NT = "<COFINS>" \
                  "<COFINSNT>" \
                    "<CST>{cst:>02}</CST>" \
                  "</COFINSNT>" \
                "</COFINS>"

    def calculate_icms(self, cst_icms, csosn, tax_item, fcp_item, base_reduction, reason, product_code):
        csosn = int(csosn)
        
        if csosn in [101]:
            return self.ICMSSN_101.format(orig=0, csosn=csosn), 0, 0, 0, 0, 0, 0
        if csosn in [102, 103, 300, 400]:
            return self.ICMSSN_102.format(orig=0, csosn=csosn), 0, 0, 0, 0, 0, 0
        elif csosn in [201]:
            return self.ICMSSN_201.format(orig=0, csosn=csosn), 0, 0, 0, 0, 0, 0
        elif csosn in [202, 203]:
            return self.ICMSSN_202.format(orig=0, csosn=csosn), 0, 0, 0, 0, 0, 0
        elif csosn in [500]:
            fcp_data = ""
            fcp_tax = 0
            fcp_tax_rate = 0
            tax_rate = tax_item.tax_rate * 100 if tax_item else 0
    
            if fcp_item and tax_item:
                fcp_data = self.ICMSSN_500_FCP.format(bc_fcp=tax_item.base_amount_ad,
                                                      p_fcp=fcp_item.tax_rate * 100,
                                                      v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad
                fcp_tax_rate = fcp_item.tax_rate * 100
    
            return self.ICMSSN_500.format(orig=0,
                                          csosn=csosn,
                                          pst=tax_rate + fcp_tax_rate,
                                          fcp_data=fcp_data), 0, 0, 0, 0, 0, fcp_tax
        elif csosn in [900]:
            return self.ICMSSN_900.format(orig=0, csosn=csosn), 0, 0, 0, 0, 0, 0
        else:
            raise Exception("CSOSN não esperado: {}. Produto: {}".format(csosn, product_code))

    def calculate_pis(self, cst_pis, tax_item):
        if cst_pis in (1, 2, 49, 99):
            return self.PIS_OUTR.format(cst=99,
                                        q_bc_prod=0,
                                        v_aliq_prod=0,
                                        v_pis=0), 0, 0
        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0
        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        if cst_cofins in (1, 2, 49, 99):
            return self.COFINS_OUTR.format(cst=99,
                                           q_bc_prod=0,
                                           v_aliq_prod=0,
                                           v_cofins=0), 0, 0
        elif cst_cofins in (4, 5, 6, 7, 8, 9):
            return self.COFINS_NT.format(cst=cst_cofins), 0, 0
        else:
            raise Exception("CST COFINS Não Esperado: %s" % cst_cofins)


class TaxBuilderSimplesNacionalSublimiteReceita(TaxBuilder):
    def __init__(self):
        super(TaxBuilderSimplesNacionalSublimiteReceita, self).__init__()

    ICMS_00 = "<ICMS>" \
                "<ICMS00>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.04f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                  "{fcp_data}" \
                  "</ICMS00>" \
                "</ICMS>"
    ICMS_00_FCP = "<pFCP>{p_fcp:.04f}</pFCP>" \
                  "<vFCP>{v_fcp:.02f}</vFCP>"

    ICMS_20 = "<ICMS>" \
                "<ICMS20>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<pRedBC>{p_red_bc:.02f}</pRedBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.04f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                  "{fcp_data}" \
                "</ICMS20>" \
              "</ICMS>"
    ICMS_20_FCP = "<vBCFCP>{bc_fcp:.02f}</vBCFCP>" \
                  "<pFCP>{p_fcp:.04f}</pFCP>" \
                  "<vFCP>{v_fcp:.02f}</vFCP>"

    ICMS_40 = "<ICMS>" \
                "<ICMS40>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "{reason_data}" \
              "</ICMS40>" \
              "</ICMS>"
    ICMS_40_REASON = "<vICMSDeson>{deson:.02f}</vICMSDeson>" \
                     "<motDesICMS>{reason}</motDesICMS>"
    ICMS_60 = "<ICMS>" \
                "<ICMS60>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "{fcp_data}" \
                  "<pRedBCEfet>0.00</pRedBCEfet>" \
                  "<vBCEfet>0.00</vBCEfet>" \
                  "<pICMSEfet>0.0000</pICMSEfet>" \
                  "<vICMSEfet>0.00</vICMSEfet>" \
              "</ICMS60>" \
              "</ICMS>"
    ICMS_60_FCP = "<vBCFCPSTRet>{bc_fcp:.02f}</vBCFCPSTRet>" \
                  "<pFCPSTRet>{p_fcp:.04f}</pFCPSTRet>" \
                  "<vFCPSTRet>{v_fcp:.02f}</vFCPSTRet>"

    PIS_OUTR = "<PIS>" \
                 "<PISOutr>" \
                   "<CST>{cst:0>2}</CST>" \
                   "<qBCProd>{q_bc_prod:.02f}</qBCProd>" \
                   "<vAliqProd>{v_aliq_prod:.04f}</vAliqProd>" \
                   "<vPIS>{v_pis:0.2f}</vPIS>" \
                 "</PISOutr>" \
               "</PIS>"
    PIS_NT = "<PIS>" \
               "<PISNT>" \
                 "<CST>{cst:>02}</CST>" \
               "</PISNT>" \
             "</PIS>"
    COFINS_OUTR = "<COFINS>" \
                    "<COFINSOutr>" \
                      "<CST>{cst:0>2}</CST>" \
                      "<qBCProd>{q_bc_prod:.02f}</qBCProd>" \
                      "<vAliqProd>{v_aliq_prod:.04f}</vAliqProd>" \
                      "<vCOFINS>{v_cofins:0.2f}</vCOFINS>" \
                    "</COFINSOutr>" \
                  "</COFINS>"
    COFINS_NT = "<COFINS>" \
                  "<COFINSNT>" \
                    "<CST>{cst:>02}</CST>" \
                  "</COFINSNT>" \
                "</COFINS>"

    def calculate_icms(self, cst_icms, csosn, tax_item, fcp_item, base_reduction, reason, product_code):
        _round_tax_amount(tax_item)
        if cst_icms in (0, ):
            fcp_data = ""
            fcp_tax = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_00_FCP.format(p_fcp=fcp_item.tax_rate * 100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad

            return self.ICMS_00.format(orig=0,
                                       cst=0,
                                       mod_bc=3,
                                       v_bc=tax_item.base_amount_ad,
                                       p_icms=tax_item.tax_rate * 100,
                                       v_icms=tax_item.tax_amount_ad,
                                       fcp_data=fcp_data), tax_item.base_amount_ad, tax_item.tax_amount_ad, 0, fcp_tax, 0, 0
        elif cst_icms in (60, ):
            fcp_data = ""
            fcp_tax = 0
            fcp_tax_rate = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_60_FCP.format(bc_fcp=tax_item.base_amount_ad,
                                                   p_fcp=fcp_item.tax_rate * 100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad
                fcp_tax_rate = fcp_item.tax_rate * 100

            return self.ICMS_60.format(orig=0,
                                       cst=cst_icms,
                                       pst=tax_item.tax_rate * 100 + fcp_tax_rate,
                                       fcp_data=fcp_data), 0, 0, 0, 0, 0, fcp_tax
        elif cst_icms in (20, ):
            fcp_data = ""
            fcp_tax = 0
            if fcp_item is not None:
                fcp_data = self.ICMS_20_FCP.format(bc_fcp=tax_item.base_amount_ad,
                                                   p_fcp=fcp_item.tax_rate * 100,
                                                   v_fcp=fcp_item.tax_amount_ad)
                fcp_tax = fcp_item.tax_amount_ad

            return self.ICMS_20.format(orig=0,
                                       cst=cst_icms,
                                       mod_bc=3,
                                       v_bc=tax_item.base_amount_ad,
                                       p_red_bc=base_reduction,
                                       p_icms=tax_item.tax_rate * 100,
                                       v_icms=tax_item.tax_amount_ad,
                                       fcp_data=fcp_data), tax_item.base_amount_ad, tax_item.tax_amount_ad, 0, fcp_tax, 0, 0
        elif cst_icms in (40, 41, 50, 51):
            return self.ICMS_40.format(orig=0,
                                       cst=cst_icms,
                                       reason_data=self.ICMS_40_REASON.format(deson=tax_item.tax_amount_ad, reason=reason) if reason else ''),\
                   0, 0, tax_item.tax_amount_ad if reason else 0, 0, 0, 0

        else:
            if not tax_item:
                raise Exception("ICMS não encontrado no produto: {}".format(product_code))
            raise Exception("CST ICMS ou taxa não esperado: {}. Produto: {}".format(cst_icms, product_code))

    def calculate_pis(self, cst_pis, tax_item):
        if cst_pis in (1, 2, 99):
            return self.PIS_OUTR.format(cst=99,
                                        q_bc_prod=0,
                                        v_aliq_prod=0,
                                        v_pis=0), 0, 0
        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0
        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        if cst_cofins in (1, 2, 99):
            return self.COFINS_OUTR.format(cst=99,
                                           q_bc_prod=0,
                                           v_aliq_prod=0,
                                           v_cofins=0), 0, 0
        elif cst_cofins in (4, 5, 6, 7, 8, 9):
            return self.COFINS_NT.format(cst=cst_cofins), 0, 0
        else:
            raise Exception("CST COFINS Não Esperado: %s" % cst_cofins)


def _round_tax_amount(tax_item):
    if tax_item:
        tax_item.base_amount_ad = round_half_away_from_zero(tax_item.base_amount_ad, 2)
        tax_item.tax_amount_ad = round_half_away_from_zero(tax_item.tax_amount_ad, 2)
