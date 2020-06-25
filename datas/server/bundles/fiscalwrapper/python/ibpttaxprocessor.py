# -*- coding: utf-8 -*-

import csv
import logging
import os
import re

from old_helper import get_sale_line_priced_items, round_half_away_from_zero
from pos_model import SaleItem
from common import FiscalParameterNotFound

logger = logging.getLogger("FiscalWrapper")


class IbptTaxProcessor(object):
    def __init__(self, mbcontext, ibpt_tax_files_path, uf, fiscal_parameter_controller):
        self.mbcontext = mbcontext
        self.ibpt_tax_files_path = ibpt_tax_files_path
        self.uf = uf
        self.ibpt_tax_dict = self._get_ibpt_tax_dict()
        self.fiscal_parameter_controller = fiscal_parameter_controller
        self.tax_types = ['nacionalfederal', 'estadual']

    def _get_ibpt_tax_dict(self):
        if os.path.isdir(self.ibpt_tax_files_path):
            ibpt_file = self._get_csv_file(self.ibpt_tax_files_path, self.uf)
            self.ibpt_tax_dict = self._convert_csv_to_dict(ibpt_file, self.ibpt_tax_files_path)
        else:
            self.ibpt_tax_dict = None

        return self.ibpt_tax_dict

    def ibpt_tax_calculator(self, order):
        if self.ibpt_tax_dict:
            product_list = self._get_order_products_ncm_list(order)
            total_taxes = self._get_total_taxes(product_list)
        else:
            total_taxes = self._get_null_taxes()

        return total_taxes

    def get_item_tax(self, sale_line):
        if self.ibpt_tax_dict:
            product_list = self._get_ncm_by_products([sale_line])
            if not product_list:
                return "0,00"

            total_taxes = self._get_total_taxes(product_list)
        else:
            total_taxes = self._get_null_taxes()

        tax_sum = sum(total_taxes[tax_type]['value'] for tax_type in total_taxes)
        return "{:.02f}".format(tax_sum)

    def _get_order_products_ncm_list(self, order):
        sale_lines = order.findall("SaleLine")
        sale_lines = get_sale_line_priced_items(sale_lines)

        return self._get_ncm_by_products(sale_lines)

    def _get_ncm_by_products(self, sale_lines):
        products = {}
        for sale_line in sale_lines:
            part_code = sale_line.part_code if type(sale_line) == SaleItem else sale_line.attrib['partCode']
            product_name = sale_line.product_name if type(sale_line) == SaleItem else sale_line.attrib['productName']
            try:
                ncm = int(self.fiscal_parameter_controller.get_parameter(int(part_code), "NCM"))
            except FiscalParameterNotFound:
                logger.warning("NCM not found: {}-{}".format(part_code, product_name))
                continue
            correct_item_price = float(sale_line.item_price if type(sale_line) == SaleItem else sale_line.attrib['correctItemPrice'])
            if ncm not in products:
                products[ncm] = correct_item_price
            else:
                products[ncm] += correct_item_price
        return products

    def _get_total_taxes(self, products):
        total_dict = {}
        for tax_type in self.tax_types:
            total_dict[tax_type] = {}
            total_value = 0
            total_tax_value = 0
            for ncm in products:
                if ncm in self.ibpt_tax_dict:
                    if self.ibpt_tax_dict[ncm][tax_type] in (None, ""):
                        tax_percent = 0
                    else:
                        tax_percent = float(self.ibpt_tax_dict[ncm][tax_type])
                    tax_value = (products[ncm] * tax_percent) / 100
                    total_value += products[ncm]
                    total_tax_value += tax_value

            if total_tax_value == 0 or total_value == 0:
                total_dict[tax_type]['value'] = 0
                total_dict[tax_type]['percent'] = 0
            else:
                total_dict[tax_type]['value'] = round_half_away_from_zero(total_tax_value, 2)
                total_dict[tax_type]['percent'] = round_half_away_from_zero(((total_tax_value * 100) / total_value), 2)

        return total_dict

    def _get_null_taxes(self):
        total_dict = {}
        for tax_type in self.tax_types:
            total_dict[tax_type] = {}
            total_dict[tax_type]['value'] = 0
            total_dict[tax_type]['percent'] = 0
        return total_dict

    @staticmethod
    def _get_csv_file(ibpt_tax_files_path, store_uf):
        csv_file = None
        for tax_file in os.listdir(ibpt_tax_files_path):
            file_uf = re.search(r"(?<=Tax)([^\d]+).*\.csv$", tax_file)
            if file_uf not in (None, "") and file_uf.group(1) == store_uf:
                csv_file = tax_file
                break
        if not csv_file:
            logger.error("IBPT Tax file not found for UF: {}".format(store_uf))
        return csv_file

    @staticmethod
    def _convert_csv_to_dict(csv_file, ibpt_tax_files_path):
        file_dict = None
        if csv_file:
            with open(os.path.join(ibpt_tax_files_path, csv_file), 'r') as f:
                reader = csv.reader(f, delimiter=';', quotechar='"')
                result = [r for r in reader]
                file_dict = {}
                for row in result[1:]:
                    result_line = {}
                    for i, item in enumerate(result[0]):
                        result_line[item] = row[i]
                        file_dict[int(row[0])] = result_line
        return file_dict
