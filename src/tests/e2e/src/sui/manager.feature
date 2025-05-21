Feature: Manager

  Scenario: Manager Options (Skim)
    When user opens POS QSR-FL-FL in mobile
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_SKIM
    And POS QSR-FL-FL sets value to 10
    And POS QSR-FL-FL checks if there's option dialog to close
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL selects the filter Sangria
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if last report value was 10,00
    Then POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_SKIM
    And POS QSR-FL-FL sets value to 100
    And POS QSR-FL-FL checks if there's option dialog to close
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL selects the filter Sangria
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if last report value was 100,00
    Then POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_SKIM
    And POS QSR-FL-FL sets value to 100000
    And POS QSR-FL-FL checks if there's option dialog to close
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL selects the filter Sangria
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if last report value was 100000,00
    Then POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Cash Paid In)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_CASH-PAID-IN
    And POS QSR-FL-FL sets value to 0 reais
    And POS QSR-FL-FL checks if there's option dialog to close
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if last report value was 0,00
    Then POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_CASH-PAID-IN
    And POS QSR-FL-FL sets value to 100 reais
    And POS QSR-FL-FL checks if there's option dialog to close
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if last report value was 100,00
    Then POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_CASH-PAID-IN
    And POS QSR-FL-FL sets value to 100000 reais
    And POS QSR-FL-FL checks if there's option dialog to close
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if last report value was 100000,00
    Then POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Void Sale)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_VOID-SALE
    And POS QSR-FL-FL checks if there is closed order to cancel then cancel it
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_MANAGE-SPECIAL-CATALOGS
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_MANAGE-SPECIAL-CATALOGS
    And POS QSR-FL-FL selects the filter HH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_MANAGE-SPECIAL-CATALOGS
    And POS QSR-FL-FL selects the filter LM
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_ManagerScreen_SALES-REPORT-BY-BUSINESS-PERIOD
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Sales Real Date)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_SALES-REAL-DATE
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Mix Business)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_MIX-BUSINESS
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_UNPRICED
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_MIX-BUSINESS
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_PRICED
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_MIX-BUSINESS
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_ALL_PRODUCTS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Interval Sales)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_INTERVAL-SALES
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Voided Lines Report)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_VOIDED-LINES-REPORT
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Voided Report)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_VOIDED-REPORT
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_PRINT
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Opened Tables)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_OPENED-TABLES
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Logoff Report)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL checks if there is logoff report
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Sales by Brand)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_SALES-BY-BRAND
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Daily Goals)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_DAILY-GOALS
    And POS QSR-FL-FL clicks on the test_DailyGoalsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Session id)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL checks if there is session id
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Delivery Report)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_DELIVERY-REPORT
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Manager Options (Discount Report)
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL clicks on the test_ManagerScreen_DISCOUNT-REPORT
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then user closes POS QSR-FL-FL

  Scenario: Check Report Value
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_TRANSFERS-REPORT
    And POS QSR-FL-FL selects the filter Sangria
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TextPreviewDialog_CLOSE
    Then user closes POS QSR-FL-FL
