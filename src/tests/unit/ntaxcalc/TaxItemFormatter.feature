# Created by ealmeida at 22/11/2017
Feature: TaxItemFormatter
  # Enter feature description here

  Scenario: When the format_tax_item is called with None, an Exception is raised
    Given the tax_item is None
    When the format_tax_item method is called
    Then an Exception from the format_tax_item method is raised

  Scenario: When the format_tax_item is called with a valid TaxItem the correct str is returned
    Given the tax_item is valid
    When the format_tax_item method is called
    Then the returned value is the correct representation of the TaxItem