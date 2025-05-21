# Created by ealmeida at 29/11/2017
Feature: ReducedBaseAmountTaxCalculator
  # Enter feature description here

  Scenario: When there are previous taxes that must reduce the base amount, the tax is calculated with the base amount
    Given there is a ReducedBaseAmountTaxCalculator created with rate = 10% and taxes_to_reduce = ['ICMS']
    When the calculate_tax method is called with a SaleItem with a item_price = 23.90 , quantity = 1 and a previous taxes with ICMS value of 0.15
    Then the TaxItem returned has tax_amount_bd and tax_amouint_ad = 2.375 and base_amount_db and base_amount_ad = 23.75