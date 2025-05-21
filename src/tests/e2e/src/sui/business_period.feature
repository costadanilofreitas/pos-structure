Feature: Business Period

  Scenario: Open business period
    When user navigates to manager menu
    And user clicks on the test_ManagerScreen_OPEN-DAY
    And user clicks on the test_MessageOptionsDialog_OK
    And user clicks on the test_MessageOptionsDialog_CLOSE

  Scenario: Close business period
    When user navigates to manager menu
    And user clicks on the test_ManagerScreen_CLOSE-DAY
    And user clicks on the test_MessageOptionsDialog_YES
