# -*- coding: utf-8 -*-

from abc import abstractmethod, ABCMeta
from old_helper import round_half_away_from_zero


class TaxBuilder(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_icms(self, cst_icms, tax_item, base_reduction):
        pass

    @abstractmethod
    def calculate_pis(self, cst_pis, tax_item):
        pass

    @abstractmethod
    def calculate_cofins(self, cst_cofins, tax_item):
        pass

    @staticmethod
    def calculate_approximated_tax_rate(ibtp_tax_processor, sale_item):
        item_approximated_tax = ibtp_tax_processor.get_item_tax(sale_item)
        return "<vItem12741>{}</vItem12741>".format(item_approximated_tax)


class TaxBuilderLucroReal(TaxBuilder):
    def __init__(self):
        super(TaxBuilder, self).__init__()

    ICMS_00 = "<ICMS>" \
                "<ICMS00>" \
                  "<Orig>{orig}</Orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<pICMS>{p_icms:.02f}</pICMS>" \
                "</ICMS00>" \
              "</ICMS>"
    ICMS_40 = "<ICMS>" \
                "<ICMS40>" \
                  "<Orig>{orig}</Orig>" \
                  "<CST>{cst:>02}</CST>" \
                "</ICMS40>" \
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
                    "</COFINSAliq>" \
                  "</COFINS>"

    def calculate_icms(self, cst_icms, tax_item, base_reduction):
        _round_tax_amount(tax_item)
        if cst_icms in (0, 20, 90) and tax_item:
            xml = self.ICMS_00.format(orig=0, cst=cst_icms, p_icms=tax_item.tax_rate * 100)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad

        elif cst_icms in (40, 41, 50, 60):
            return self.ICMS_40.format(orig=0, cst=cst_icms), 0, 0

        else:
            raise Exception("CST ICMS Não Esperado: %s" % cst_icms)

    def calculate_pis(self, cst_pis, tax_item):
        _round_tax_amount(tax_item)
        if cst_pis in (1, 2) and tax_item:
            xml = self.PIS_ALIQ.format(cst=cst_pis, v_bc=tax_item.base_amount_ad, p_pis=tax_item.tax_rate)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad

        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0

        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        _round_tax_amount(tax_item)
        if cst_cofins in (1, 2) and tax_item:
            xml = self.COFINS_ALIQ.format(cst=cst_cofins, v_bc=tax_item.base_amount_ad, p_cofins=tax_item.tax_rate)
            return xml, tax_item.base_amount_ad, tax_item.tax_amount_ad

        elif cst_cofins in (4, 5, 6, 7, 8, 9):
            return self.COFINS_NT.format(cst=cst_cofins), 0, 0

        else:
            raise Exception("CST COFINS Não Esperado: %s" % cst_cofins)


class TaxBuilderSimplesNacional(TaxBuilder):
    def __init__(self):
        super(TaxBuilderSimplesNacional, self).__init__()

    ICMSSN_500 = "<ICMS>" \
                   "<ICMSSN500>" \
                     "<Orig>{orig}</Orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN500>" \
                 "</ICMS>"
    ICMSSN_102 = "<ICMS>" \
                   "<ICMSSN102>" \
                     "<Orig>{orig}</Orig>" \
                     "<CSOSN>{csosn}</CSOSN>" \
                   "</ICMSSN102>" \
                 "</ICMS>"
    PIS_SN = "<PIS>" \
               "<PISSN>" \
                 "<CST>{cst:0>2}</CST>" \
               "</PISSN>"\
              "</PIS>"
    PIS_NT = "<PIS>" \
               "<PISNT>" \
                 "<CST>{cst:>02}</CST>" \
               "</PISNT>" \
             "</PIS>"
    COFINS_SN = "<COFINS>" \
                  "<COFINSSN>" \
                    "<CST>{cst:0>2}</CST>" \
                  "</COFINSSN>"\
                "</COFINS>"
    COFINS_NT = "<COFINS>" \
                  "<COFINSNT>" \
                    "<CST>{cst:>02}</CST>" \
                  "</COFINSNT>" \
                "</COFINS>"

    def calculate_icms(self, cst_icms, tax_item, base_reduction):
        if cst_icms in (0, 20, 90):
            return self.ICMSSN_102.format(orig=0, csosn=102), 0, 0
        elif cst_icms in (60, ):
            return self.ICMSSN_102.format(orig=0, csosn=500), 0, 0
        else:
            raise Exception("CST ICMS Não Esperado: %s" % cst_icms)

    def calculate_pis(self, cst_pis, tax_item):
        if cst_pis in (1, 2):
            return self.PIS_SN.format(cst=49), 0, 0
        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0
        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        if cst_cofins in (1, 2):
            return self.COFINS_SN.format(cst=49), 0, 0
        elif cst_cofins in (4, 5, 6, 7, 8, 9):
            return self.COFINS_NT.format(cst=cst_cofins), 0, 0
        else:
            raise Exception("CST COFINS Não Esperado: %s" % cst_cofins)


class TaxBuilderSimplesNacionalSublimiteReceita(TaxBuilder):
    def __init__(self):
        super(TaxBuilderSimplesNacionalSublimiteReceita, self).__init__()

    ICMS_00 = "<ICMS>" \
                "<ICMS00>" \
                  "<Orig>{orig}</Orig>" \
                  "<CST>{cst:>02}</CST>" \
                  "<pICMS>{p_icms:.02f}</pICMS>" \
                  "</ICMS00>" \
                "</ICMS>"
    ICMS_40 = "<ICMS>" \
                "<ICMS40>" \
                  "<Orig>{orig}</Orig>" \
                  "<CST>{cst:>02}</CST>" \
                "</ICMS40>" \
              "</ICMS>"
    PIS_OUTR = "<PIS>" \
                 "<PISOutr>" \
                   "<CST>{cst:0>2}</CST>" \
                   "<qBCProd>{q_bc_prod:.02f}</qBCProd>" \
                   "<vAliqProd>{v_aliq_prod:.04f}</vAliqProd>" \
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
                    "</COFINSOutr>" \
                  "</COFINS>"
    COFINS_NT = "<COFINS>" \
                  "<COFINSNT>" \
                    "<CST>{cst:>02}</CST>" \
                  "</COFINSNT>" \
                "</COFINS>"

    def calculate_icms(self, cst_icms, tax_item, base_reduction):
        _round_tax_amount(tax_item)

        if cst_icms in (0, 20, 90):
            return self.ICMS_00.format(orig=0,
                                       cst=0,
                                       p_icms=tax_item.tax_rate * 100), tax_item.base_amount_ad, tax_item.tax_amount_ad
        elif cst_icms in (40, 41, 50, 60):
            self.ICMS_40.format(orig=0, cst=cst_icms), 0, 0
            #else:
            #    return self.ICMS_400.format(), 0, 0
        else:
            raise Exception("CST ICMS Não Esperado: %s" % cst_icms)

    def calculate_pis(self, cst_pis, tax_item):
        if cst_pis in (1, 2):
            return self.PIS_OUTR.format(cst=99,
                                        q_bc_prod=0,
                                        v_aliq_prod=0), 0, 0
        elif cst_pis in (4, 5, 6, 7, 8, 9):
            return self.PIS_NT.format(cst=cst_pis), 0, 0
        else:
            raise Exception("CST PIS Não Esperado: %s" % cst_pis)

    def calculate_cofins(self, cst_cofins, tax_item):
        if cst_cofins in (1, 2):
            return self.COFINS_OUTR.format(cst=99,
                                           q_bc_prod=0,
                                           v_aliq_prod=0), 0, 0
        elif cst_cofins in (4, 5, 6, 7, 8, 9):
            return self.COFINS_NT.format(cst=cst_cofins), 0, 0
        else:
            raise Exception("CST COFINS Não Esperado: %s" % cst_cofins)


def _round_tax_amount(tax_item):
    if tax_item:
        tax_item.base_amount_ad = round_half_away_from_zero(tax_item.base_amount_ad, 2)
        tax_item.tax_amount_ad = round_half_away_from_zero(tax_item.tax_amount_ad, 2)
