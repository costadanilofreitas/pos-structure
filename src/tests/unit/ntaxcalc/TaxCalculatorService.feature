# Created by ealmeida at 22/11/2017
Feature: TaxCalculatorService
  # Enter feature description here

  Scenario: The received order is parsed with the OrderParser
    Given there is a mocked OrderParser
    And there is a mocked GeneralTaxCalculator
    And there is a mocked OrderFormatter
    When the calculate_taxes method is called
    Then the parse_order method of the OrderParsed is called with the received order

  Scenario: Every SaleItem returned from the parser is passed to the GeneralTaxCalculator
    Given there is a mocked OrderParser
    And there is a mocked GeneralTaxCalculator
    And there is a mocked OrderFormatter
    When the calculate_taxes method is called
    Then the calculate_all_taxes method of the GeneralTaxCalculator is called with every SaleItem returned from the OrderParser

  Scenario: The values returned from the calculate_all_taxes are added to the tax_items of the order and the order is passed to the order_formatter
    Given there is a mocked OrderParser
    And there is a mocked GeneralTaxCalculator
    And there is a mocked OrderFormatter
    When the calculate_taxes method is called
    Then the order is passed to the OrderFormatter with the tax_items property filled with the calculated taxes

  Scenario: The value returned from the OrderFormatter is returned
    Given there is a mocked OrderParser
    And there is a mocked GeneralTaxCalculator
    And there is a mocked OrderFormatter
    When the calculate_taxes method is called
    Then the return value is equal to the value returned from the OrderFormatter

  Scenario: Any Exception from the parse_order is reraised
    Given there is a mocked OrderParser that raised an Exception
    And there is a mocked GeneralTaxCalculator
    And there is a mocked OrderFormatter
    When the calculate_taxes method is called
    Then the exception risen from the OrderParser is raised by the TaxCalculatorService

  Scenario: Any Exception from the GeneralTaxCalculator is reraised
    Given there is a mocked OrderParser
    And there is a mocked GeneralTaxCalculator that raises an Exception
    And there is a mocked OrderFormatter
    When the calculate_taxes method is called
    Then the exception risen from the OrderParser is raised by the TaxCalculatorService