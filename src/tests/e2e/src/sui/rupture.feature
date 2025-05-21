Feature: Rupture

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
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL checks if product CHX QUESADILHA HALF is ruptured
    And POS QSR-FL-FL checks if product CHX QUESADILHA REGULAR is ruptured
    And POS QSR-FL-FL checks if product CHX QUESADILHA GENEROUS is ruptured
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL clicks the element with text 49909 - FRANGO
    And POS QSR-FL-FL clicks on the test_RuptureDialog_ENABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_RuptureDialog_SAVE
    And POS QSR-FL-FL clicks on the test_RuptureConfirmation_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL checks if product CHX QUESADILHA HALF is not ruptured
    And POS QSR-FL-FL checks if product CHX QUESADILHA REGULAR is not ruptured
    And POS QSR-FL-FL checks if product CHX QUESADILHA GENEROUS is not ruptured
    And user closes POS QSR-FL-FL

  Scenario: Multiple selection
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL clicks the element with text 10129 - BONELESS  SAMPLER
    And POS QSR-FL-FL clicks the element with text 10130 - BUFFALO SAMPLER
    And POS QSR-FL-FL clicks the element with text 10131 - CHX QUESADILLAS SAMPLER
    And POS QSR-FL-FL clicks on the test_RuptureDialog_DISABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if item 10129 - BONELESS SAMPLER is in rupture
    And POS QSR-FL-FL checks if item 10130 - BUFFALO SAMPLER is in rupture
    And POS QSR-FL-FL checks if item 10131 - CHX QUESADILLAS SAMPLER is in rupture
    And POS QSR-FL-FL clicks on the test_RuptureDialog_SAVE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if item 10129 - BONELESS SAMPLER is in rupture enter
    And POS QSR-FL-FL checks if item 10130 - BUFFALO SAMPLER is in rupture enter
    And POS QSR-FL-FL checks if item 10131 - CHX QUESADILLAS SAMPLER is in rupture enter
    And POS QSR-FL-FL clicks on the test_RuptureConfirmation_BACK
    And POS QSR-FL-FL clicks on the test_RuptureDialog_CLOSE
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL checks if item 10129 - BONELESS SAMPLER is not in rupture
    And POS QSR-FL-FL checks if item 10130 - BUFFALO SAMPLER is not in rupture
    And POS QSR-FL-FL checks if item 10131 - CHX QUESADILLAS SAMPLER is not in rupture
    And POS QSR-FL-FL clicks on the test_RuptureDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Rupture scroll
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL clicks on the test_ScrollPanel_DOWN
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_ScrollPanel_UP
    And POS QSR-FL-FL clicks on the test_RuptureDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Rupture keyboard filter
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL send input Frango to keyboard
    And POS QSR-FL-FL delete text
    And POS QSR-FL-FL send input Agua to keyboard
    And POS QSR-FL-FL delete text
    And POS QSR-FL-FL send input Pepsi to keyboard
    And POS QSR-FL-FL delete text
    And POS QSR-FL-FL clicks on the test_RuptureDialog_CLOSE
    And user closes POS QSR-FL-FL

  Scenario: Rupture keyboard show button
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_MANAGER-MENU
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    And POS QSR-FL-FL clicks on the test_ManagerScreen_RUPTURE
    And POS QSR-FL-FL clicks on the test_KeyboardWrapper_KEYBOARD-SHOW
    And POS QSR-FL-FL send input PEPSI to keyboard
    And POS QSR-FL-FL clicks on the test_KeyboardWrapper_KEYBOARD-SHOW
    And POS QSR-FL-FL clicks on the test_RuptureDialog_CLOSE
    And user closes POS QSR-FL-FL
