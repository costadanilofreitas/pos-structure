Feature: Mobile Sale

  Background: Reset Skim
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Mobile saves products in every sale type available
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to order tab
    Then mobile POS QSR-FL-FL saves products in every sale type available
    Then user closes POS QSR-FL-FL

  Scenario: Payment Options
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And mobile POS QSR-FL-FL sets quantity to 15
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds CHOPP COLORADO APPIA 500 ML to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTALORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL enters name Fernanda if needed
    Then POS QSR-FL-FL tests all payment options
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Sell a product
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTALORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL enters name Fernanda if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's TAX is equal to 0,00
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 11,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 11,90
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Cancel order
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FL-FL waits 2 seconds
    And POS QSR-FL-FL clicks on the test_FilterableList_OK    And POS QSR-FL-FL checks if there's option dialog to click ok
    Then user closes POS QSR-FL-FL

  Scenario: Set quantity over 100
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL waits 2 seconds
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And mobile POS QSR-FL-FL sets quantity to 150
    And POS QSR-FL-FL waits 2 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 2 seconds
    Then user closes POS QSR-FL-FL

  Scenario: Set quantity to nothing
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And POS QSR-FL-FL clicks on the test_MobileQtyButtonsRenderer_QTY
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    Then user closes POS QSR-FL-FL
