Feature: Totem

  Scenario: Cancel order
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order BUDWEISER
    Then POS TOTEM checks if order's TOTAL is equal to 11,90
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: ADD and REMOVE order item
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order BUDWEISER
    And POS TOTEM clicks on the test_TotemItemOptions_ADD
    And POS TOTEM checks if there's element 2 BUDWEISER on screen
    And POS TOTEM CLicks on the test_TotemItemOptions_MINUS
    And POS TOTEM checks if there's element 1 BUDWEISER on screen
    Then POS TOTEM checks if order's TOTAL is equal to 11,90
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: Empty cart
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order BUDWEISER
    Then POS TOTEM checks if order's TOTAL is equal to 11,90
    Then POS TOTEM clicks on the test_SaleSummary_CLEAN
    Then POS TOTEM checks if order's TOTAL is equal to 0,00
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: Modify order
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    Then POS TOTEM clicks on the test_TotemItemOptions_MODIFY
    And  POS TOTEM select order COLAR
    Then POS TOTEM checks if order's TOTAL is equal to 17,98
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: Navigation options
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order PRATOS
    And POS TOTEM checks if there's element PRATOS on screen
    And  POS TOTEM select order ENTRADAS
    And POS TOTEM checks if there's element ENTRADAS on screen
    And  POS TOTEM select order CAMPANHA
    And POS TOTEM checks if there's element CAMPANHA on screen
    And  POS TOTEM select order BEBIDAS
    And POS TOTEM checks if there's element BEBIDAS on screen
    And  POS TOTEM select order BUDWEISER
    Then POS TOTEM checks if order's TOTAL is equal to 11,90
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: Payment options (Credit)
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    Then POS TOTEM checks if order's TOTAL is equal to 17,98
    And POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM send input Camila to keyboard
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_SaleSummaryScreen_NEXT
    And POS TOTEM clicks on the test_TotemTendersRenderer_CREDIT
    And POS TOTEM checks if dialog text is Confirma recebimento em TEF Credito: R$ 17,98
    And POS TOTEM clicks on the test_MessageOptionsDialog_OK
    And POS TOTEM clicks on the test_MessageOptionsDialog_YES
    Then user closes POS TOTEM

  Scenario: Payment options (Debit)
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    And POS TOTEM waits 1 seconds
    Then POS TOTEM checks if order's TOTAL is equal to 17,98
    And POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM send input Camila to keyboard
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_SaleSummaryScreen_NEXT
    And POS TOTEM clicks on the test_TotemTendersRenderer_DEBIT
    And POS TOTEM checks if dialog text is Confirma recebimento em TEF Debito: R$ 17,98
    And POS TOTEM clicks on the test_MessageOptionsDialog_OK
    And POS TOTEM clicks on the test_MessageOptionsDialog_YES
    Then user closes POS TOTEM

  Scenario: Costumer Name and CPF
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    And POS TOTEM waits 1 seconds
    Then POS TOTEM checks if order's TOTAL is equal to 17,98
    And POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS TOTEM send input 46466603857 to numpad
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM send input Camila to keyboard
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_SaleSummaryScreen_NEXT
    And POS TOTEM clicks on the test_TenderScreenRenderer_CHANGE-NAME
    And POS TOTEM delete text
    And POS TOTEM send input Renata to keyboard
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_TenderScreenRenderer_CHANGE-DOCUMENT
    And POS TOTEM clicks on the test_NumPad_CLEAR
    And POS TOTEM send input 37209061835 to numpad
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM clicks on the test_TotemTendersRenderer_DEBIT
    And POS TOTEM checks if dialog text is Confirma recebimento em TEF Debito: R$ 17,98
    And POS TOTEM clicks on the test_MessageOptionsDialog_OK
    And POS TOTEM clicks on the test_MessageOptionsDialog_YES
    Then user closes POS TOTEM

  Scenario: Back button
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    And POS TOTEM waits 1 seconds
    Then POS TOTEM checks if order's TOTAL is equal to 17,98
    And POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS TOTEM send input 46466603857 to numpad
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM send input Camila to keyboard
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_SaleSummaryScreen_BACK
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: Check Tender Screen Total
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    And POS TOTEM waits 1 seconds
    Then POS TOTEM checks if order's TOTAL is equal to 17,98
    And POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM send input Camila to keyboard
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_SaleSummaryScreen_NEXT
    And POS TOTEM checks if total is TOTAL A PAGAR R$ 17,98
    And POS TOTEM clicks on the test_TenderScreenRenderer_BACK
    And POS TOTEM clicks on the test_SaleSummaryScreen_BACK
    And POS TOTEM clicks on the test_SaleSummary_CANCEL
    Then user closes POS TOTEM

  Scenario: Check Confirmation Screen
    When user opens POS TOTEM in totem
    Then POS TOTEM clicks on the test_WelcomeScreen_CONTAINER
    Then POS TOTEM clicks on the test_saleTypeScreen_EAT-IN
    And  POS TOTEM select order CHOPP BRAHMA 500 ML
    And POS TOTEM clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS TOTEM clicks on the test_NumPadDialog_OK
    And POS TOTEM clicks on the test_KeyboardDialog_OK
    And POS TOTEM clicks on the test_SaleSummaryScreen_NEXT
    And POS TOTEM clicks on the test_TotemTendersRenderer_DEBIT
    And POS TOTEM clicks on the test_MessageOptionsDialog_OK
    And POS TOTEM clicks on the test_MessageOptionsDialog_YES
    And Totem checks confirmation screen timeout
    Then user closes POS TOTEM
