# Created by eduardo at 17/11/2017
Feature: FixedRateTaxCalculator
  # Enter feature description here

  Scenario: When called with SaleItem the TaxItem is returned with the calculated tax
    Given there is a FixedTaxCalculator with the tax value of 10% created
    When the calculate_tax method is called with a SaleItem with a item_price = 23.90 , quantity = 1
    Then the ItemTax returned has tax_amount_bd and tax_amouint_ad = 2.39 and base_amount_db and base_amount_ad = 23.9

  Scenario: When called with product in the SaleItem that is not registered, None is returned
    Given there is a FixedTaxCalculator with the tax value of 10% created
    When the calculate_tax method is called with a not registered SaleItem with a item_price = 10.90 , quantity = 1
    Then None is returned

  Scenario: When called with SaleItem with quantity = 3 the TaxItem is returned with the correct calculated taxes
    Given there is a FixedTaxCalculator with the tax value of 10% created
    When the calculate_tax method is called with SaleItem with a item_price = 10.90 , quantity = 3
    Then the ItemTax returned has tax_amount_bd and tax_amouint_ad = 3.27 and base_amount_db and base_amount_ad = 32.7

  Scenario: When called with None as SaleItem, an Exception is risen
    Given there is a FixedTaxCalculator with the tax value of 10% created
    When the calculate_tax method is called with None
    Then an Exception is risen

  Scenario: When called with a SaleItem with discount the TaxItem is returned with the calculated tax
    Given there is a FixedTaxCalculator with the tax value of 10% created
    When the calculate_tax method is called with with a SaleItem with a item_price = 23.90, item_discount = 2.39, quantity = 1
    Then the ItemTax returned has tax_amount_bd and tax_amount_ad = 2.151 and base_amount_db = 23.9 and base_amount_ad = 21.51