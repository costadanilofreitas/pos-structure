# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta

from old_helper import round_half_away_from_zero
import logging

logger = logging.getLogger("FiscalWrapper")

class TaxBuilder(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def calculate_icms(self, cst_icms, tax_item, base_reduction, reason):
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
                "</ICMS00>" \
              "</ICMS>"
    ICMS_20 = "<ICMS>" \
                "<ICMS20>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<pRedBC>{p_red_bc:.02f}</pRedBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.04f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                "</ICMS20>" \
              "</ICMS>"
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
                  "<pRedBCEfet>0.00</pRedBCEfet>" \
                  "<vBCEfet>0.00</vBCEfet>" \
                  "<pICMSEfet>0.0000</pICMSEfet>" \
                  "<vICMSEfet>0.00</vICMSEfet>" \
              "</ICMS60>" \
              "</ICMS>"
    ICMS_90 = "<ICMS>" \
                "<ICMS90>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.02f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                "</ICMS90>" \
              "</ICMS>"
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

    def calculate_icms(self, cst_icms, tax_item, base_reduction, reason):
        # returns xml line, base amount, tax amount and deson
        _round_tax_amount(tax_item)
        if cst_icms == 0 and tax_item:
            xml = self.ICMS_00.format(orig=0,
                                      cst=cst_icms,
                                      mod_bc=3,
                                      v_bc=tax_item.base_amount_ad,
                                      p_icms=tax_item.tax_rate * 100,
                                      v_icms=tax_item.tax_amount_ad)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad, 0

        elif cst_icms == 20 and tax_item:
            xml = self.ICMS_20.format(orig=0,
                                      cst=cst_icms,
                                      mod_bc=3,
                                      v_bc=tax_item.base_amount_ad,
                                      p_red_bc=base_reduction,
                                      p_icms=tax_item.tax_rate * 100,
                                      v_icms=tax_item.tax_amount_ad)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad, 0

        elif cst_icms == 40 and tax_item:
            if tax_item.tax_amount_ad > 0:
                logger.warning("CST ICMS = 40, tax amount maior que zero")
            if not reason:
                logger.warning("CST ICMS = 40, não possui motivo, usando padrão 9")
                reason = "9"
            xml = self.ICMS_40.format(orig=0,
                                      cst=cst_icms,
                                      reason_data=self.ICMS_40_REASON.format(deson=tax_item.tax_amount_ad, reason=reason) if reason else '')
            return xml, 0, 0, tax_item.tax_amount_ad if reason else 0

        elif cst_icms == 60:
            if tax_item.tax_amount_ad > 0:
                logger.warning("CST ICMS = 60, tax amount maior que zero")

            xml = self.ICMS_60.format(orig=0, cst=cst_icms)
            return xml, 0, 0, 0

        elif cst_icms == 90:
            xml = self.ICMS_90.format(orig=0,
                                      cst=cst_icms,
                                      mod_bc=3,
                                      v_bc=tax_item.base_amount_ad,
                                      p_icms=tax_item.tax_rate * 100,
                                      v_icms=tax_item.tax_amount_ad)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad, 0

        else:
            raise Exception("CST ICMS ou taxa Não Esperado: %s" % cst_icms)

    def calculate_pis(self, cst_pis, tax_item):
        _round_tax_amount(tax_item)
        if cst_pis in (1, 2) and tax_item:
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
        if cst_cofins in (1, 2) and tax_item:
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

    ICMSSN_500 = "<ICMS>" \
                   "<ICMSSN500>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                     "<pRedBCEfet>0.00</pRedBCEfet>" \
                     "<vBCEfet>0.00</vBCEfet>" \
                     "<pICMSEfet>0.0000</pICMSEfet>" \
                     "<vICMSEfet>0.00</vICMSEfet>" \
                 "</ICMSSN500>" \
                 "</ICMS>"
    ICMSSN_102 = "<ICMS>" \
                   "<ICMSSN102>" \
                     "<orig>{orig}</orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN102>" \
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

    def calculate_icms(self, cst_icms, tax_item, base_reduction, reason):
        if cst_icms in (0, ):
            return self.ICMSSN_102.format(orig=0, csosn=102), 0, 0, 0
        elif cst_icms in (60, ):
            return self.ICMSSN_500.format(orig=0, csosn=500), 0, 0, 0
        elif cst_icms in (20, ):
            return self.ICMSSN_102.format(orig=0, csosn=102), 0, 0, 0
        elif cst_icms in (40, 41, 50, 51):
            return self.ICMSSN_102.format(orig=0, csosn=102), 0, 0, 0
        else:
            raise Exception("CST ICMS Não Esperado: %s" % cst_icms)
            #else:
            #    return self.ICMS_400.format(), 0, 0

    def calculate_pis(self, cst_pis, tax_item):
        if cst_pis in (1, 2):
            return self.PIS_OUTR.format(cst=99,
                                        q_bc_prod=0,
                                        v_aliq_prod=0,
                                        v_pis=0), 0, 0
        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0
        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        if cst_cofins in (1, 2):
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
                  "</ICMS00>" \
                "</ICMS>"
    ICMS_20 = "<ICMS>" \
                "<ICMS20>" \
                  "<orig>{orig}</orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<modBC>{mod_bc}</modBC>" \
                  "<pRedBC>{p_red_bc:.02f}</pRedBC>" \
                  "<vBC>{v_bc:.02f}</vBC>" \
                  "<pICMS>{p_icms:.04f}</pICMS>" \
                  "<vICMS>{v_icms:.02f}</vICMS>" \
                "</ICMS20>" \
              "</ICMS>"
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
                  "<pRedBCEfet>0.00</pRedBCEfet>" \
                  "<vBCEfet>0.00</vBCEfet>" \
                  "<pICMSEfet>0.0000</pICMSEfet>" \
                  "<vICMSEfet>0.00</vICMSEfet>" \
              "</ICMS60>" \
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

    def calculate_icms(self, cst_icms, tax_item, base_reduction, reason):
        _round_tax_amount(tax_item)
        if cst_icms in (0, ):
            return self.ICMS_00.format(orig=0,
                                       cst=0,
                                       mod_bc=3,
                                       v_bc=tax_item.base_amount_ad,
                                       p_icms=tax_item.tax_rate * 100,
                                       v_icms=tax_item.tax_amount_ad), tax_item.base_amount_ad, tax_item.tax_amount_ad
        elif cst_icms in (60, ):
            return self.ICMS_60.format(orig=0, cst=cst_icms), 0, 0, 0
        elif cst_icms in (20, ):
            return self.ICMS_20.format(orig=0,
                                       cst=cst_icms,
                                       mod_bc=3,
                                       v_bc=tax_item.base_amount_ad,
                                       p_red_bc=base_reduction,
                                       p_icms=tax_item.tax_rate * 100,
                                       v_icms=tax_item.tax_amount_ad), tax_item.base_amount_ad, tax_item.tax_amount_ad
        elif cst_icms in (40, 41, 50, 51):
            return self.ICMS_40.format(orig=0,
                                       cst=cst_icms,
                                       reason_data=self.ICMS_40_REASON.format(deson=tax_item.tax_amount_ad, reason=reason) if reason else ''),\
                   0, 0, tax_item.tax_amount_ad if reason else 0
            #else:
            #    return self.ICMS_400.format(), 0, 0
        else:
            raise Exception("CST ICMS Não Esperado: %s" % cst_icms)

    def calculate_pis(self, cst_pis, tax_item):
        if cst_pis in (1, 2):
            return self.PIS_OUTR.format(cst=99,
                                        q_bc_prod=0,
                                        v_aliq_prod=0,
                                        v_pis=0), 0, 0
        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0
        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        if cst_cofins in (1, 2):
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
