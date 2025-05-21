Feature: EXPO/PREP

  Background: Reset Skim
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Removed Modifier Text
    When user opens POS QSR-FL-FL in desktop
    Then user opens PREP prep-chapa
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY-ORDER
    And POS QSR-FL-FL clicks the element with text BACON
    And POS QSR-FL-FL checks if there's element SEM BACON on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS prep-chapa waits 1 seconds
    And POS prep-chapa checks if there's element SEM on screen
    And POS prep-chapa waits 1 seconds
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element SEM on screen
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS prep-chapa
    Then user closes POS EXPO

  Scenario: EXPO/PREP - Cancel Order With Greater Prep Time
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    Then user opens PREP prep-frito
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 2 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL adds MOZZARELLA HALF to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And KDS EXPO checks if order does contains tag TIME
    And POS EXPO waits 1 seconds
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_OPTIONS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks the element with text 1 CHX QUESADILHA HALF
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if there's element 1 MOZZARELLA HALF on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And KDS EXPO checks if order doesnt contains tag TIME
    And POS EXPO waits 1 seconds
    And POS prep-frito checks if there's element MOZZARELLA HALF on screen
    And KDS EXPO serves all orders
    Then user closes POS prep-frito
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: TAKE OUT - Order Ignoring Course
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SaleType_TAKE-OUT
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL clicks on the test_SubMenu_SOBREMESAS
    And POS QSR-FL-FL adds CHURROS REGULAR to order
    And POS QSR-FL-FL clicks the element with text NUTELLA
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    Then user opens EXPO
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element CAESAR REGULAR on screen
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element CHX QUESADILHA HALF on screen
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element CHURROS REGULAR on screen
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: DRIVE THRU - Order Ignoring Course
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SaleType_DRIVE-THRU
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL clicks on the test_SubMenu_SOBREMESAS
    And POS QSR-FL-FL adds CHURROS REGULAR to order
    And POS QSR-FL-FL clicks the element with text NUTELLA
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    Then user opens EXPO
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element CAESAR REGULAR on screen
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element CHX QUESADILHA HALF on screen
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element CHURROS REGULAR on screen
    And KDS EXPO serves all orders
    Then user closes POS EXPO
