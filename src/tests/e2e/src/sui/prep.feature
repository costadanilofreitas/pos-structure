Feature: PREP

  Background: Reset Skim
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Check ready order
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    When user opens PREP prep-frito
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL enters name Fernanda if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS prep-frito clicks on the test_MainScreen_TAB-0
    And POS prep-frito clicks on the test_ActionsRenderer_DONE
    And POS prep-frito clicks on the test_MainScreen_TAB-2
    And POS prep-frito checks if there's element ORIENTAL REGULAR on screen
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO
    Then user closes POS prep-frito

  Scenario: Canceled Line not disappearing on PREP
    When user opens POS QSR-FL-FL in desktop
    Then user opens PREP prep-frito
    When user opens EXPO
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds BONELESS BUFFALO WINGS HALF to order
    And POS QSR-FL-FL adds BUFFALO CHICKEN WINGS HALF to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS prep-frito waits 3 seconds
    And POS prep-frito checks if there's element BONELESS BUFFALO WINGS HALF on screen
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS EXPO waits 3 seconds
    And KDS EXPO serves all orders
    Then user closes POS prep-frito
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: PREP Order's Threshold
    When user opens POS QSR-FL-FL in desktop
    When user opens PREP prep-frito
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL enters name Fernanda if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS prep-frito clicks on the test_MainScreen_TAB-0
    And POS prep-frito checks thresholds
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS prep-frito
    Then user closes POS EXPO

  Scenario: PREP - Cancel order with greater prep time
    When user opens POS QSR-FL-FL in desktop
    When user opens PREP prep-frito
    When user opens PREP prep-chapa
    When user opens EXPO
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
    Then POS prep-frito checks if there isn't element MOZZARELLA HALF on screen
    Then POS prep-chapa checks if there's element CHX QUESADILHA HALF on screen
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_OPTIONS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks the element with text 1 CHX QUESADILHA HALF
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL waits 1 seconds
    Then POS prep-frito checks if there's element MOZZARELLA HALF on screen
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And KDS EXPO serves all orders
    Then user closes POS prep-frito
    Then user closes POS prep-chapa
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: PREP - Table order grouping items
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 2 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL waits 1 seconds

    And POS QSR-FL-FL clicks on the test_QtyButtonsRenderer_2
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds CHX QUESADILHA HALF to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    When user opens PREP prep-chapa
    Then POS prep-chapa checks if there's element 6 on screen
    Then POS prep-chapa checks if there's element CHX QUESADILHA HALF on screen
    Then user closes POS prep-chapa
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: PREP - Consolidate Items showing products correctly
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds SUMMER SALAD SIDE to order
    And POS QSR-FL-FL adds ORIENTAL SIDE to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL    Then user opens PREP prep-frito
    And POS prep-frito clicks on the test_FooterRenderer_LIST
    Then POS prep-frito checks if there's element SUMMER SALAD SIDE on screen
    Then POS prep-frito checks if there's element ORIENTAL SIDE on screen
    Then user closes POS prep-frito
    Then user opens EXPO
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO