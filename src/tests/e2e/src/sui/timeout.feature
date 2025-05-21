Feature: Timeout

  Scenario: POS QSR-FL-FL - Order Screen Timeout
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to ORDER tab
    Then POS QSR-FL-FL checks timeout popup
    Then user closes POS QSR-FL-FL

  Scenario: POS QSR-FL-FL - Table Screen Timeout
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to TABLE tab
    Then POS QSR-FL-FL checks timeout popup
    Then user closes POS QSR-FL-FL

  Scenario: POS QSR-FL-FL - Recall Screen Timeout
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to RECALL tab
    Then POS QSR-FL-FL checks timeout popup
    Then user closes POS QSR-FL-FL

  Scenario: POS QSR-FL-FL - Operator Screen Timeout
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    Then POS QSR-FL-FL checks timeout popup
    Then user closes POS QSR-FL-FL

  Scenario: POS QSR-FL-FL - Recall Screen Timeout
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to RECALL tab
    Then POS QSR-FL-FL authenticates the operator 1000 if needed
    Then POS QSR-FL-FL checks timeout popup
    Then user closes POS QSR-FL-FL

  Scenario: POS TOTEM - SaleType Screen Timeout
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then Totem checks sale type timeout
    Then user closes POS TOTEM

  Scenario: POS TOTEM - Order Screen Timeout
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    Then POS TOTEM checks timeout popup
    Then user closes POS TOTEM

  Scenario: POS TOTEM - Tender Screen Timeout
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    Then Totem adds CHOPP BRAHMA 330 ML to order
    And POS TOTEM waits 1 seconds
    Then POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    Then POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    Then POS TOTEM checks timeout popup
    Then user closes POS TOTEM
