Feature: Pickup

  Scenario: Auto command
    When user opens POS QSR-FL-FL in desktop
    When user opens PICKUP
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL stores order id
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 3 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO
    And PICKUP checks order in Ready Box
    And POS PICKUP waits auto order command
    Then user closes POS PICKUP

  Scenario: Check PICKUP columns
    When user opens POS QSR-FL-FL in desktop
    When user opens PICKUP
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL stores order id
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL waits 1 seconds
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 3 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO
    Then user closes POS PICKUP

  Scenario: Check customer name
    When user opens POS QSR-FL-FL in desktop
    When user opens PICKUP
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderActionsRenderer_COSTUMER-NAME
    And POS QSR-FL-FL send input TESTE to keyboard
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO
    And POS PICKUP checks if there's element TESTE on screen
    Then user closes POS PICKUP

  Scenario: Table order must not appear
    When user opens PICKUP
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 2 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL stores order id
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And PICKUP checks if stored order is not on screen
    Then user closes POS PICKUP
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Pickup thresholds
    When user opens POS QSR-FL-FL in desktop
    When user opens PICKUP
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_BEBIDAS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL stores order id
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    And POS PICKUP waits auto order command
    Then user closes POS PICKUP
