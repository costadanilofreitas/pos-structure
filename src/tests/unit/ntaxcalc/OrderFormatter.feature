# Created by ealmeida at 22/11/2017
Feature: OrderFormater
  # Enter feature description here

  Scenario: Every TaxItem is formatted with the TaxItemFormatter
    Given there is a mocked TaxItemFormatter
    And there is a mocked Order
    When the format_order method of the OrderFormatter is called
    Then the format_tax_item is called for every TaxItem

  Scenario: The returned formatted order is correct
    Given there is a mocked TaxItemFormatter
    And there is a mocked Order
    When the format_order method of the OrderFormatter is called
    Then the returned formatted order is correct