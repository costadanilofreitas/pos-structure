# Created by eduardo at 17/11/2017
Feature: General TaxCalculator
  # Enter feature description here

  Scenario: When the calculate_taxes method is called, all taxes calculators are called in order
    Given there is a GeneralTaxCalculator initialized with three mocked TaxCalculators
    When the calculate_tax method is called with a SaleItem
    Then all three mocked TaxCalculators are called in order

  Scenario: When the calculate_taxes method is called, the later TaxCalculator received the previous tax calculations
    Given there is a GeneralTaxCalculator initialized with three mocked TaxCalculators
    When the calculate_tax method is called with a SaleItem
    Then the first TaxCalculator must be called with an empty list
    And the second TaxCalculator must be called with a list with the previous tax calculation
    And the third TaxCalculator must be called with a list with the two previous tax calculations

  Scenario: When the calculate_taxes method is called the return value is a list with all tax calculations
    Given there is a GeneralTaxCalculator initialized with three mocked TaxCalculators
    When the calculate_tax method is called with a SaleItem
    Then the return value is a list with all tax calculations

  Scenario: If the TaxCalculator calculate_tax method returnd None, it is not added to the list of TaxItens
    Given there is a GeneralTaxCalculator initialized with one TaxCalculator that always returns None
    When the calculate_tax method is called with a SaleItem
    Then the return value is an empty list