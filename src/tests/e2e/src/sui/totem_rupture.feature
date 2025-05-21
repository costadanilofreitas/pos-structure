Feature: Totem Rupture

  Scenario: Add item to rupture then remove it
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL send input Frango to keyboard
    And POS QSR-FL-FL clicks the element with text 49909 - FRANGO
    And POS QSR-FL-FL clicks on the test_RuptureDialog_DISABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_RuptureDialog_SAVE
    And POS QSR-FL-FL clicks on the test_RuptureConfirmation_OK
    Then user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    And POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And POS TOTEM clicks on the test_SubMenu_ENTRADAS
    And POS TOTEM checks if product CHX QUESADILHA GENEROUS is ruptured
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL clicks the element with text 49909 - FRANGO
    And POS QSR-FL-FL clicks on the test_RuptureDialog_ENABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_RuptureDialog_SAVE
    And POS QSR-FL-FL clicks on the test_RuptureConfirmation_OK
    And POS QSR-FL-FL waits 1 seconds
    Then Totem checks if it is at welcome screen
    And POS TOTEM clicks on the test_SubMenu_ENTRADAS
    And POS TOTEM checks if product CHX QUESADILHA GENEROUS is not ruptured
    And user closes POS QSR-FL-FL
    And user closes POS TOTEM