# -*- coding: utf-8 -*-

from typing import Dict, Any
from xml.sax.saxutils import escape
from pos_model import Order

from pos_model import TaxItem, SaleItem
from common import FiscalParameterController
from pos_util import SaleLineUtil

from _SatXmlPartBuilder import SatXmlPartBuilder
from _ContextKeys import ContextKeys
from _TaxBuilder import TaxBuilderLucroReal, TaxBuilderSimplesNacional, TaxBuilderSimplesNacionalSublimiteReceita


class DetBuilder(SatXmlPartBuilder):
    def __init__(self, crt, fiscal_parameter_controller, sale_line_util, ibtp_tax_processor):
        # type: (int, FiscalParameterController, SaleLineUtil, IbptTaxProcessor) -> None
        self.crt = crt
        self.fiscal_parameter_controller = fiscal_parameter_controller
        self.sale_line_util = sale_line_util
        self.ibtp_tax_processor = ibtp_tax_processor
        if crt == 1:
            self.tax_builder = TaxBuilderSimplesNacional()
        elif crt == 2:
            self.tax_builder = TaxBuilderSimplesNacionalSublimiteReceita()
        elif crt == 3:
            self.tax_builder = TaxBuilderLucroReal()
        else:
            raise Exception("CRT Não informado")

    def build_xml(self, order, context):
        # type: (Order, Dict[unicode, Any]) -> unicode
        item_no = context[ContextKeys.item_no]  # type: int
        sale_item = context[ContextKeys.current_sale_item]  # type: SaleItem

        cest = self.fiscal_parameter_controller.get_optional_parameter(sale_item.part_code, "CEST")

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

        product_name = escape(sale_item.product_name)

        cest_xml = "" if cest is None else "<obsFiscoDet xCampoDet='Cod.CEST'><xTextoDet>{x_text_det:>07}</xTextoDet></obsFiscoDet>".format(x_text_det=cest)

        prod_xml_template = "<prod>" \
                            "<cProd>{c_prod}</cProd>" \
                            "<xProd>{x_prod}</xProd>" \
                            "<NCM>{ncm:0>8}</NCM>" \
                            "<CFOP>{cfop}</CFOP>" \
                            "<uCom>UN</uCom>" \
                            "<qCom>{q_com:0.4f}</qCom>" \
                            "<vUnCom>{v_un_com:0.3f}</vUnCom>" \
                            "<indRegra>A</indRegra>"\
                            "{discount_xml}" \
                            "{cest_xml}" \
                            "</prod>"
        prod_xml = prod_xml_template.format(
            c_prod=sale_item.part_code,
            x_prod=product_name.strip(),
            ncm=int(ncm),
            cfop=cfop,
            q_com=sale_item.quantity,
            v_un_com=sale_item.unit_price or sale_item.added_unit_price,
            discount_xml="<vDesc>{:.02f}</vDesc>".format(sale_item.item_discount or 0.0),
            cest_xml=cest_xml
        )

        impost_xml_template = "<imposto>{tax_xml}</imposto>"


        v_item_12741 = self.tax_builder.calculate_approximated_tax_rate(self.ibtp_tax_processor, sale_item)
        tax_xml = v_item_12741

        icms_tax_item = sale_item.get_tax_item("ICMS")  # type: TaxItem
        xml, vbc, icms_tax = self.tax_builder.calculate_icms(cst_icms, icms_tax_item, base_reduction)
        tax_xml += xml
        parcial_vbc = vbc

        pis_tax_item = sale_item.get_tax_item("PIS")  # type: TaxItem
        xml, vbc, pis_tax = self.tax_builder.calculate_pis(cst_pis, pis_tax_item)
        tax_xml += xml

        cofins_tax_item = sale_item.get_tax_item("COFINS")  # type: TaxItem
        xml, vbc, cofins_tax = self.tax_builder.calculate_cofins(cst_cofins, cofins_tax_item)
        tax_xml += xml

        imposto_xml = impost_xml_template.format(tax_xml=tax_xml)

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

        return xml
