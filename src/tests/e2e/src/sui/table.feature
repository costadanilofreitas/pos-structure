Feature: Table

  Background: Reset Skim
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Open table without and with over 100 seats
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if dialog text is O número de pessoas deve ser maior que 0
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 1000 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if dialog text is Número acima que o máximo de assentos permitidos
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Change table order - Delete line
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_OPTIONS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks the element with text 1 BUDWEISER
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if there's element 1 MALZEBIER on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Add order in an open table, cancel it then abandon table
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Open tab without number
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_NumPadDialog_CANCEL
    Then user closes POS QSR-FL-FL

  Scenario: Open tab 1, add order, cancel it then abandon tab
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL checks if dialog text is Confirma envio sem informação adicional?
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_TABS
    And POS QSR-FL-FL selects tab 1
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Open table from map view then abandon it
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in map view
    And POS QSR-FL-FL clicks on the test_FloorPlan_15
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Join empty tables and abandon them
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABLES
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABLES
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 8 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Join tables containing orders
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABLES
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 35,70
    And POS QSR-FL-FL checks if order's TIP is equal to 3,57
    And POS QSR-FL-FL checks if order's TOTAL is equal to 39,27
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 39,27
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 39,27
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Join tabs
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL send input 10 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL checks if dialog text is Confirma envio sem informação adicional?
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL send input 11 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's TIP is equal to 1,19
    And POS QSR-FL-FL checks if order's TOTAL is equal to 13,09
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 13,09
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,09
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Join tab in a table
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL send input 12 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL checks if dialog text is Confirma envio sem informação adicional?
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABS
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 7 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's TIP is equal to 1,19
    And POS QSR-FL-FL checks if order's TOTAL is equal to 13,09
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 13,09
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,09
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Transfer order to an open table
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_TRANSFER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 35,70
    And POS QSR-FL-FL checks if order's TIP is equal to 3,57
    And POS QSR-FL-FL checks if order's TOTAL is equal to 39,27
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 39,27
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 39,27
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Transfer order to a seated table
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_DESELECT
    And POS QSR-FL-FL clicks on the test_TableStateFilter_IN_PROGRESS
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_TRANSFER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 35,70
    And POS QSR-FL-FL checks if order's TIP is equal to 3,57
    And POS QSR-FL-FL checks if order's TOTAL is equal to 39,27
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 39,27
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 39,27
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Transfer order from tab
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_TABS
    And POS QSR-FL-FL selects tab 1
    And POS QSR-FL-FL clicks on the test_TableActions_TRANSFER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Table order functions
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in map view
    Then POS QSR-FL-FL clicks on the test_FloorPlan_15
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    Then POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 35,70
    And POS QSR-FL-FL checks if there's element 1 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SELECTED-SEAT
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL checks if there's element 2 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SELECTED-SEAT
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL checks if there's element 3 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SELECTED-SEAT
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    And POS QSR-FL-FL checks if there's element 4 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL adds CAIP CACHAÇA TRADICIONAL to order
    And POS QSR-FL-FL clicks on the test_ProductButton_MORANGO
    And POS QSR-FL-FL checks if order's TOTAL is equal to 19,90
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL selects MORANGO from the order's modifiers
    And POS QSR-FL-FL clicks on the test_OrderFunctions_CLEAR-OPTION
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_ONSIDE
    And POS QSR-FL-FL clicks on the test_ProductButton_MARACUJA
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY-ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_1
    And POS QSR-FL-FL clicks on the test_ProductButton_ADOÇANTE
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_MINUS
    And POS QSR-FL-FL clicks on the test_ProductButton_AÇUCAR
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_LIGHT
    And POS QSR-FL-FL clicks on the test_ProductButton_AÇUCAR
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_EXTRA
    And POS QSR-FL-FL clicks on the test_ProductButton_ADOÇANTE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY-ORDER
    And POS QSR-FL-FL checks if there's element (DIVIDIDO) ADOÇANTE on screen
    And POS QSR-FL-FL checks if there's element (POUCO) AÇUCAR on screen
    And POS QSR-FL-FL checks if there's element (AO LADO) MARACUJA on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY-ORDER
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SEAT-CHANGE
    And POS QSR-FL-FL selects the filter Sem Assento
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SEAT-CHANGE
    And POS QSR-FL-FL selects the filter Assento 1
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 1 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SEAT-CHANGE
    And POS QSR-FL-FL selects the filter Assento 2
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 2 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SEAT-CHANGE
    And POS QSR-FL-FL selects the filter Assento 3
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 3 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SEAT-CHANGE
    And POS QSR-FL-FL selects the filter Assento 4
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 4 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_FloorPlan_15
    Then POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 19,90
    And POS QSR-FL-FL checks if order's TIP is equal to 1,99
    And POS QSR-FL-FL checks if order's TOTAL is equal to 21,89
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 21,89
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 21,89
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Table seats options
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableListScreenRenderer_SEARCH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 2 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL checks if order's TOTAL is equal to 11,90
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_SEAT-CHANGE
    And POS QSR-FL-FL selects the filter Sem Assento
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then POS QSR-FL-FL clicks on the test_TableListScreenRenderer_SEARCH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    Then POS QSR-FL-FL clicks on the test_TableActions_CHANGESEATS
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    Then POS QSR-FL-FL clicks on the test_TableActions_REORGANIZE
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_CHANGE-SEATS
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_LOCK-OPEN
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 1 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 2 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 3 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 4 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 5 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 6 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 0 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_SPLIT
    And POS QSR-FL-FL send input 5 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL selects 5 parts of the BUDWEISER
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_MERGE
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_SPLIT
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 1 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 2 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 3 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 4 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 5 from rearrange seats
    Then POS QSR-FL-FL selects the product BUDWEISER from seats
    And POS QSR-FL-FL selects the seat 6 from rearrange seats
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_CHANGE-SEATS
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_LOCK
    And POS QSR-FL-FL clicks on the test_TableSeatsActions_BACK
    Then POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,89
    And POS QSR-FL-FL checks if order's TIP is equal to 1,19
    And POS QSR-FL-FL checks if order's TOTAL is equal to 13,08
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 13,08
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,08
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Payment options
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableListScreenRenderer_SEARCH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL sets quantity to 10
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL clicks on the test_TableListScreenRenderer_SEARCH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    Then POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 130,90
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_TableActions_TOTALREPORT
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABLE
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then POS QSR-FL-FL clicks on the test_TableActions_TOTALREPORT
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_SEATS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_CLOSE
    Then POS QSR-FL-FL pays 5 reais in cash
    And POS QSR-FL-FL checks if order's DINHEIRO is equal to 5,00
    And POS QSR-FL-FL checks if order's PAID is equal to 5,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 125,90
    Then POS QSR-FL-FL clicks on the test_TableActions_CLEARTENDERS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_OrderTender_10
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL checks if order's DINHEIRO is equal to 10,00
    And POS QSR-FL-FL checks if order's PAID is equal to 10,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 120,90
    And POS QSR-FL-FL clicks on the test_TableActions_CLEARTENDERS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_OrderTender_20
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL checks if order's DINHEIRO is equal to 20,00
    And POS QSR-FL-FL checks if order's PAID is equal to 20,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 110,90
    And POS QSR-FL-FL clicks on the test_TableActions_CLEARTENDERS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_OrderTender_50
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL checks if order's DINHEIRO is equal to 50,00
    And POS QSR-FL-FL checks if order's PAID is equal to 50,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 80,90
    And POS QSR-FL-FL clicks on the test_TableActions_CLEARTENDERS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_OrderTender_100
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL checks if order's DINHEIRO is equal to 100,00
    And POS QSR-FL-FL checks if order's PAID is equal to 100,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 30,90
    And POS QSR-FL-FL clicks on the test_TableActions_CLEARTENDERS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_OrderTender_APPLY_DISCOUNTS
    And POS QSR-FL-FL selects the filter 1 - Valor
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 25 reais
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's DISCOUNT is equal to 25,00
    And POS QSR-FL-FL checks if order's TOTAL_AFTER_DISCOUNT is equal to 94,00
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 105,90
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 105,90
    Then POS QSR-FL-FL clicks on the test_OrderTender_APPLY_DISCOUNTS
    And POS QSR-FL-FL selects the filter 2 - Porcentagem
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL sets value to 10 reais
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's DISCOUNT is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL_AFTER_DISCOUNT is equal to 107,10
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 119,00
    Then POS QSR-FL-FL clicks on the test_OrderTender_CLEAN_DISCOUNTS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's TOTAL is equal to 130,90
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    Then POS QSR-FL-FL clicks on the test_TableActions_CHANGETIP
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 25 percent
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 29,75
    And POS QSR-FL-FL checks if order's TOTAL is equal to 148,75
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 148,75
    Then POS QSR-FL-FL clicks on the test_TableActions_CHANGETIP
    And POS QSR-FL-FL selects the filter Valor
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 25 reais
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 25,00
    And POS QSR-FL-FL checks if order's TOTAL is equal to 144,00
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 144,00
    And POS QSR-FL-FL clicks on the test_TableActions_REOPEN
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Open table with quick access button and then abandon it
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableListScreenRenderer_SEARCH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_DESELECT
    And POS QSR-FL-FL clicks on the test_TableListScreenRenderer_SEARCH
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL
