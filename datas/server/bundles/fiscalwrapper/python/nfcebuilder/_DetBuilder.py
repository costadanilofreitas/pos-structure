# -*- coding: utf-8 -*-

from xml.sax.saxutils import escape

from _ContextKeys import ContextKeys
from _NfceXmlPartBuilder import NfceXmlPartBuilder
from _TaxBuilder import TaxBuilderLucroReal, TaxBuilderSimplesNacional, TaxBuilderSimplesNacionalSublimiteReceita
from common import FiscalParameterController, FiscalParameterNotFound
from pos_model import Order
from pos_model import TaxItem, SaleItem
from pos_util import SaleLineUtil
from typing import Dict, Any


class DetBuilder(NfceXmlPartBuilder):
    def __init__(self, ambiente, crt, fiscal_parameter_controller, sale_line_util, versao_ws):
        # type: (unicode, int, FiscalParameterController, SaleLineUtil, int) -> None
        self.versao_ws = versao_ws
        self.ambiente = ambiente
        self.crt = crt
        self.fiscal_parameter_controller = fiscal_parameter_controller
        self.sale_line_util = sale_line_util

        if self.crt == 1:
            self.tax_builder = TaxBuilderSimplesNacional()
        elif self.crt == 2:
            self.tax_builder = TaxBuilderSimplesNacionalSublimiteReceita()
        elif self.crt == 3:
            self.tax_builder = TaxBuilderLucroReal()
        else:
            raise Exception("CRT Não informado")

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        item_no = context[ContextKeys.item_no]  # type: int
        sale_item = context[ContextKeys.current_sale_item]  # type: SaleItem

        cest = self.fiscal_parameter_controller.get_optional_parameter(sale_item.part_code, "CEST")
        cBenef = self.fiscal_parameter_controller.get_optional_parameter(sale_item.part_code, "cBenef")

        ncm = self.fiscal_parameter_controller.get_parameter(sale_item.part_code, "NCM")
        if ncm is None:
            raise Exception("NCM Não encontrado\\%s-%s" % (sale_item.part_code, sale_item.product_name))
        cfop = self.fiscal_parameter_controller.get_parameter(sale_item.part_code, "CFOP")
        if cfop is None:
            raise Exception("CFOP Não encontrado\\%s-%s" % (sale_item.part_code, sale_item.product_name))

        cst_icms = int(self.fiscal_parameter_controller.get_parameter(sale_item.part_code, "CST_ICMS"))
        if cst_icms is None:
            raise Exception("CST ICMS Não encontrado\\%s-%s" % (sale_item.part_code, sale_item.product_name))
        cst_pis = int(self.fiscal_parameter_controller.get_parameter(sale_item.part_code, "CST_PIS"))
        if cst_pis is None:
            raise Exception("CST PIS Não encontrado\\%s-%s" % (sale_item.part_code, sale_item.product_name))
        cst_cofins = int(self.fiscal_parameter_controller.get_parameter(sale_item.part_code, "CST_COFINS"))
        if cst_cofins is None:
            raise Exception("CST COFINS Não encontrado\\%s-%s" % (sale_item.part_code, sale_item.product_name))
        base_reduction = float(self.fiscal_parameter_controller.get_optional_parameter(sale_item.part_code, "BASE_REDUCTION") or 0)

        cst_reason = self.fiscal_parameter_controller.get_optional_parameter(sale_item.part_code, "CST_REASON")


        if self.ambiente == '1':
            product_name = escape(sale_item.product_name).strip()
        else:
            product_name = "NOTA FISCAL EMITIDA EM AMBIENTE DE HOMOLOGACAO - SEM VALOR FISCAL"

        cest_xml = "" if cest is None else "<CEST>{cest:>07}</CEST>".format(cest=cest)
        c_benef = "" if cBenef is None or cst_icms == 0 else "<cBenef>{cBenef}</cBenef>".format(cBenef=cBenef)

        prod_xml_template = "<prod>" \
                            "<cProd>{c_prod}</cProd>" \
                            "{c_ean}" \
                            "<xProd>{x_prod}</xProd>" \
                            "<NCM>{ncm:0>8}</NCM>" \
                            "{cest_xml}" \
                            "{c_benef}" \
                            "<CFOP>{cfop}</CFOP>" \
                            "<uCom>UN</uCom>" \
                            "<qCom>{q_com:0.4f}</qCom>" \
                            "<vUnCom>{v_un_com:0.3f}</vUnCom>" \
                            "<vProd>{v_prod:.02f}</vProd>" \
                            "{c_ean_trib}" \
                            "<uTrib>{u_trib}</uTrib>" \
                            "<qTrib>{q_trib}</qTrib>" \
                            "<vUnTrib>{v_un_trib}</vUnTrib>" \
                            "{discount}" \
                            "<indTot>{ind_tot}</indTot>" \
                            "</prod>"
        prod_xml = prod_xml_template.format(
            c_prod=sale_item.part_code,
            c_ean="<cEAN>SEM GTIN</cEAN>" if self.versao_ws not in (1, 3) else "<cEAN/>",
            x_prod=product_name,
            ncm=int(ncm),
            cest_xml=cest_xml,
            c_benef=c_benef,
            cfop=cfop,
            q_com=sale_item.quantity,
            v_un_com=sale_item.unit_price or sale_item.added_unit_price,
            v_prod=sale_item.item_price,
            c_ean_trib="<cEANTrib>SEM GTIN</cEANTrib>" if self.versao_ws not in (1, 3) else "<cEANTrib/>",
            u_trib="UN",
            q_trib=sale_item.quantity,
            v_un_trib=sale_item.unit_price or sale_item.added_unit_price,
            discount="<vDesc>{:.02f}</vDesc>".format(sale_item.item_discount) if sale_item.item_discount else "",
            ind_tot=1
        )

        parcial_imposto_atual = 0

        impost_xml_template = "<imposto><vTotTrib>{v_tot_trib:0.2f}</vTotTrib>{tax_xml}</imposto>"

        icms_tax_item = sale_item.get_tax_item("ICMS")  # type: TaxItem
        xml, vbc, icms_tax, deson = self.tax_builder.calculate_icms(cst_icms, icms_tax_item, base_reduction, cst_reason)
        tax_xml = xml
        parcial_vbc = vbc
        parcial_imposto_atual += icms_tax

        pis_tax_item = sale_item.get_tax_item("PIS")  # type: TaxItem
        xml, vbc, pis_tax = self.tax_builder.calculate_pis(cst_pis, pis_tax_item)
        tax_xml += xml
        parcial_imposto_atual += pis_tax

        cofins_tax_item = sale_item.get_tax_item("COFINS")  # type: TaxItem
        xml, vbc, cofins_tax = self.tax_builder.calculate_cofins(cst_cofins, cofins_tax_item)
        tax_xml += xml
        parcial_imposto_atual += cofins_tax

        imposto_xml = impost_xml_template.format(v_tot_trib=parcial_imposto_atual, tax_xml=tax_xml)

        xml = "<det nItem=\"{0}\">{prod_xml}{imposto_xml}</det>".format(
            item_no,
            prod_xml=prod_xml,
            imposto_xml=imposto_xml
        )

        context[ContextKeys.total_cofins] += cofins_tax
        context[ContextKeys.total_icms] += icms_tax
        context[ContextKeys.total_pis] += pis_tax
        context[ContextKeys.total_prod] += sale_item.item_price
        context[ContextKeys.total_vbc] += parcial_vbc
        if ContextKeys.deson not in context:
            context[ContextKeys.deson] = 0
        context[ContextKeys.deson] += deson

        return xml
