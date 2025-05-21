# Created by ealmeida at 22/11/2017
Feature: NTaxCalcEventHandler
  # Enter feature description here

  Scenario: When handle event is called with a invalid subject the calculate_tax method is not called
    Given there is a mocked tax_calculator_service
    And there is a mocked MBContext
    And an invalid subject will be called
    When the handle_event method is called
    Then there are no calls on the calculate_tax method

  Scenario: When handle event is called with a TAX_CALC subject the calculate_tax method is called
    Given there is a mocked tax_calculator_service
    And there is a mocked MBContext
    And an TAX_CALC subject will be called
    When the handle_event method is called
    Then the calculate_taxes is called with the data of the event
    And the response from calculate_taxes is replied to the message bus

  Scenario: Any exception from the calculate_taxes is handled and logged
    Given there is a mocked tax_calculator_service that raises an Exception
    And there is a mocked MBContext
    And an TAX_CALC subject will be called
    And there is a mocked logger
    When the handle_event method is called
    Then an NACK is sent on the message bus
    And the exception is logged