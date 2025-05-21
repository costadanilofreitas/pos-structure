Feature: Reports

  Scenario: Test sales report by business period
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to manager-menu tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_SALES-REPORT-BY-BUSINESS-PERIOD
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    Then POS QSR-FL-FL the system store the sales report data
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
