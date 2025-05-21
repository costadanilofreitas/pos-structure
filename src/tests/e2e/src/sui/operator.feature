Feature: Operator

  Scenario: Open new day
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL checks if needs to close day
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_ManagerScreen_OPEN-DAY
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if needs to print
    And user closes POS QSR-FL-FL

  Scenario: Open operator
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Close operator
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    And user closes POS QSR-FL-FL

  Scenario: Operator Options (Sales Business)
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_SALES-BUSINESS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Operator Options (Tip Report)
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_TIP-REPORT
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Operator Options (Mix Business)
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_MIX-BUSINESS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_UNPRICED
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_MIX-BUSINESS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_PRICED
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_MIX-BUSINESS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_ALL_PRODUCTS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Operator Options (Interval Sales)
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_INTERVAL-SALES
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Operator Options (Daily Goal)
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_DAILY-GOAL
    And POS QSR-FL-FL clicks on the test_DailyGoalsDialog_OK
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_OPERATOR-CLOSING
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Close Operators (TS)
    When user opens POS TS-FL-FL in desktop
    Then POS TS-FL-FL checks if needs to change to OPERATOR tab
    And POS TS-FL-FL waits 1 seconds
    Then POS TS-FL-FL authenticates the operator 4 if needed
    And POS TS-FL-FL clicks on the test_Header_PANEL
    And POS TS-FL-FL clicks on the test_Header_OPERATOR
    And POS TS-FL-FL waits 1 seconds
    Then POS TS-FL-FL authenticates the operator 5 if needed
    And POS TS-FL-FL waits 1 seconds
    And POS TS-FL-FL clicks on the test_Header_MANAGER-MENU
    And POS TS-FL-FL waits 1 seconds
    And POS TS-FL-FL authenticates the operator 1000 if needed
    And POS TS-FL-FL waits 1 seconds
    And POS TS-FL-FL clicks on the test_ManagerScreen_CLOSE-OPERATORS
    And POS TS-FL-FL close operator
    And POS TS-FL-FL waits 1 seconds
    And POS TS-FL-FL clicks on the test_ManagerScreen_CLOSE-OPERATORS
    And POS TS-FL-FL close operator
    And user closes POS TS-FL-FL

  Scenario: Change Operator (TS|QSR)
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And user closes POS QSR-FL-FL
    When user opens POS TS-FL-FL in desktop
    And POS TS-FL-FL clicks on the test_Header_OPERATOR
    And POS TS-FL-FL waits 1 seconds
    Then POS TS-FL-FL authenticates the operator 4 if needed
    And POS TS-FL-FL clicks on the test_Header_PANEL
    And POS TS-FL-FL clicks on the test_Header_OPERATOR
    And POS TS-FL-FL waits 1 seconds
    Then POS TS-FL-FL authenticates the operator 5 if needed
    And POS TS-FL-FL waits 1 seconds
    Then POS TS-FL-FL checks if needs to change to table tab
    And POS TS-FL-FL checks if it's in table view
    And POS TS-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS TS-FL-FL selects first table
    And POS TS-FL-FL send input 6 to NumPad
    And POS TS-FL-FL clicks on the test_NumPadDialog_OK
    And POS TS-FL-FL clicks on the test_TableActions_ADDORDER
    And POS TS-FL-FL sets quantity to 3
    And POS TS-FL-FL adds BUDWEISER to order
    And POS TS-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS TS-FL-FL selects first table
    And POS TS-FL-FL clicks on the test_TableActions_CHANGEOPERATOR
    And POS TS-FL-FL authenticates the operator 1000 if needed
    And POS TS-FL-FL clicks on the test_FilterableList_OK
    And POS TS-FL-FL clicks on the test_MessageOptionsDialog_YES
    And user closes POS TS-FL-FL
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_TableItem_TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_Header_OPERATOR
    Then POS QSR-FL-FL clicks on the test_OperatorScreen_CLOSE-USER
    And POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL checks if there's bordereau and closes it
    And POS QSR-FL-FL checks if needs to justify
    Then user closes POS QSR-FL-FL
    When user opens POS TS-FL-FL in desktop
    And POS TS-FL-FL clicks on the test_Header_MANAGER-MENU
    And POS TS-FL-FL authenticates the operator 1000 if needed
    And POS TS-FL-FL waits 1 seconds
    And POS TS-FL-FL clicks on the test_ManagerScreen_CLOSE-OPERATORS
    And POS TS-FL-FL close operator
    And POS TS-FL-FL waits 1 seconds
    And POS TS-FL-FL clicks on the test_ManagerScreen_CLOSE-OPERATORS
    And POS TS-FL-FL close operator
    And user closes POS TS-FL-FL
