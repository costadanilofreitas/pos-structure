# Created by ealmeida at 21/11/2017
Feature: OrderParser
  # Enter feature description here

  Scenario: When called with a single product the correct SaleItem is created
    When the parse_order is called with an order with just one product with quantity = 1
    And the parse_order method is called
    Then a list with a single SaleItem is created

  Scenario: When called with a single product the correct orderId and posId are returned
    When the parse_order is called with an order with just one product with quantity = 1
    And the parse_order method is called
    Then the correct orderId and posId are returned

  Scenario: When called with a single multiplied product the correct SaleItem is created
    When the parse_order is called with an order with just one product with quantity = 3
    And the parse_order method is called
    Then a list with a single multiplied SaleItem is created

  Scenario: When called with a caddadd the correct SaleItems are returned
    When the parse_order is called with an order with a combo and a canadd
    And the parse_order method is called
    Then a list with a all the SaleItems of the canadd are returned

  Scenario: When called with an ingredient the correct SaleItems are returned
    When the order has a combo with a product with ingredients
    And the parse_order method is called
    Then a list with a all the SaleItems of the product and ingredients are returned

  Scenario: The discount in the SaleLine is correcly parsed
    When the parse_order is called with an order with a combo and a canadd with discount
    And the parse_order method is called
    Then a list with a all the SaleItems of the canadd are returned with the correct discount