# -*- coding: utf-8 -*-
import os

from helper import config_logger, import_pydevd
from old_helper import get_class_by_name
from messagehandler import MessageHandler
from msgbus import MBEasyContext
from pos_model import OrderParser

from eventhandler import NTaxCalcEventHandler
from taxcalculator import TaxCalculatorService, GeneralTaxCalculator, OrderFormatter, TaxItemFormatter
from taxcalculator.repository import NTaxCalcRepository

REQUIRED_SERVICES = ""


def main():
    import_pydevd(os.environ["LOADERCFG"], 9175)

    config_logger(os.environ["LOADERCFG"], 'NTaxCalc')
    mbcontext = MBEasyContext("NTaxCalc")

    message_handler = MessageHandler(mbcontext, "NTaxCalc", "NTaxCalc", REQUIRED_SERVICES)

    order_parser = OrderParser()

    tax_calculators = []
    ntaxcalc_repository = NTaxCalcRepository(mbcontext)

    taxes = ntaxcalc_repository.load_all_taxes()
    for tax in taxes:
        tax_products = ntaxcalc_repository.load_all_products_from_tax(tax.code)

        klz = get_class_by_name(tax.tax_processor)
        tax_calculator = klz(mbcontext, tax.code, tax.name, tax.fiscal_index, tax.rate, tax_products, tax.params)

        tax_calculators.append(tax_calculator)

    general_tax_calculator = GeneralTaxCalculator(tax_calculators)

    tax_item_formatter = TaxItemFormatter()
    order_formatter = OrderFormatter(tax_item_formatter)
    tax_calculator_service = TaxCalculatorService(order_parser, general_tax_calculator, order_formatter)

    event_handler = NTaxCalcEventHandler(mbcontext, tax_calculator_service)

    message_handler.set_event_handler(event_handler)

    message_handler.subscribe_sync_events(["TAXCALC", "TAX_CALC"])

    message_handler.handle_events()
