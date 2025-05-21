Feature: Sale

  Background: Reset Skim
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Skim blocking sale
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL adds products until skim level 3
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Caixa travado, necessario fazer a Sangria
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Caixa travado, necessario fazer a Sangria
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Checks Barcode Screen Item
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL clicks on the test_SubMenu_null
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if there's element 2150015 on screen
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_SubMenu_null
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if there isn't element 2150015 on screen
    And POS QSR-FL-FL waits 1 seconds
    Then user closes POS QSR-FL-FL

  Scenario: Apply Discount - VALUE
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_APPLY_DISCOUNTS
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 5
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Apply Discount - PERCENTAGE
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_APPLY_DISCOUNTS
    And POS QSR-FL-FL clicks the element with text 2 - Porcentagem
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 5
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Sell a product receiving cash without change
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_QtyButtonsRenderer_SELECTOR
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL sets quantity to 150
    And POS QSR-FL-FL checks if dialog text is Quantidade máxima de itens excedida
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL sets quantity to 2
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 23,80
    And POS QSR-FL-FL sets quantity to 1
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 35,70
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 35,70
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Payment Options
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And POS QSR-FL-FL sets quantity to 15
    And POS QSR-FL-FL adds CHOPP COLORADO APPIA 500 ML to order
    And POS QSR-FL-FL waits 3 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    Then POS QSR-FL-FL tests all payment options
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL checks if there's option dialog to click yes
    Then user closes POS QSR-FL-FL

  Scenario: Check modify order screen
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_SOBREMESAS
    And POS QSR-FL-FL adds CHURROS REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOID-ORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL adds SHOOTER SUNDAE and pay
    Then user closes POS QSR-FL-FL

  Scenario: Cancel order
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL sets quantity to 5
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 59,50
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOID-ORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Add order, delete line, add commentary, modify and then total
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL adds BOHEMIA PILSEN to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL sets quantity to 5
    And POS QSR-FL-FL adds BOHEMIA PILSEN to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 59,50
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SPECIAL-INSTRUCTION
    And POS QSR-FL-FL send input Teste de comentário to keyboard
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOID-ORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Save product in every sale type available
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL saves products in every sale type available
    Then user closes POS QSR-FL-FL

  Scenario: Change table order - Add Comment to first line
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to order tab
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL clicks the element with text 1 BUDWEISER
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SPECIAL-INSTRUCTION
    And POS QSR-FL-FL send input Teste de Comentario to keyboard
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks the element with text 1 MALZEBIER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if there's element Teste de Comentario on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOID-ORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's option dialog to click ok
    Then user closes POS QSR-FL-FL
