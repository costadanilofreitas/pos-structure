Feature: Mobile Table

  Background: Reset Skim
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Open table without and over 100 seats
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if dialog text is O número de pessoas deve ser maior que 0
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 0 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if dialog text is O número de pessoas deve ser maior que 0
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 100 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL checks if dialog text is Número acima que o máximo de assentos permitidos
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL

  Scenario: Open table, add order and then total it
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's TAX is equal to 0,00
    And POS QSR-FL-FL checks if order's TIP is equal to 1,19
    And POS QSR-FL-FL checks if order's TOTAL is equal to 13,09
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 13,09
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,09
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL

  Scenario: Open tab, add order, cancel it, add another order and then total it
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableOrderHeader_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL waits 0.5 seconds
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds MALZEBIER to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's TAX is equal to 0,00
    And POS QSR-FL-FL checks if order's TIP is equal to 1,19
    And POS QSR-FL-FL checks if order's TOTAL is equal to 13,09
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 13,09
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,09
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL

  Scenario: Join tables and tabs with orders then total them
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL adds BUDWEISER to order
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 23,80
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_OpenTabs_CREATE-TAB
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 23,80
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_KeyboardDialog_OK
    And POS QSR-FL-FL checks if dialog text is Confirma envio sem informação adicional?
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And mobile POS QSR-FL-FL opens table 12
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_OPTIONS
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABLES
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 10 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_JOIN
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_TABS
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 11 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 47,60
    And POS QSR-FL-FL checks if order's TAX is equal to 0,00
    And POS QSR-FL-FL checks if order's TIP is equal to 4,76
    And POS QSR-FL-FL checks if order's TOTAL is equal to 52,36
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 52,36
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 52,36
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL

  Scenario: Transfer order to another table
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_OPTIONS
    And POS QSR-FL-FL clicks on the test_TableActions_TRANSFER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 11,90
    And POS QSR-FL-FL checks if order's TAX is equal to 0,00
    And POS QSR-FL-FL checks if order's TIP is equal to 1,19
    And POS QSR-FL-FL checks if order's TOTAL is equal to 13,09
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 13,09
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,09
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL

  Scenario: Mobile all table order functions
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 4 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if there's element 1 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETELINE
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderFunctions_INCREMENTSEAT
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if there's element 2 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETELINE
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderFunctions_INCREMENTSEAT
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if there's element 3 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETELINE
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderFunctions_INCREMENTSEAT
    And POS QSR-FL-FL adds BRAHMA ZERO to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 11,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 11,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if there's element 4 on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETELINE
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_NavigationPageRenderer_BACK
    And POS QSR-FL-FL clicks on the test_NavigationPageRenderer_BACK
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CAIPIRINHAS MARGARIT
    And POS QSR-FL-FL adds CAIP CACHAÇA TRADICIONAL to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 19,90
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 19,90
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL checks if dialog text is Você precisa resolver as opções do item: CAIP CACHAÇA TRADICIONAL
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_ONSIDE
    And POS QSR-FL-FL clicks the element with text MARACUJA
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_1
    And POS QSR-FL-FL clicks the element with text ADOÇANTE
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_MINUS
    And POS QSR-FL-FL clicks the element with text AÇUCAR
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_LIGHT
    And POS QSR-FL-FL clicks the element with text AÇUCAR
    And POS QSR-FL-FL clicks on the test_ItemModifierRenderer_EXTRA
    And POS QSR-FL-FL clicks the element with text ADOÇANTE
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if there's element (DIVIDIDO) ADOÇANTE on screen
    And POS QSR-FL-FL checks if there's element (POUCO) AÇUCAR on screen
    And POS QSR-FL-FL checks if there's element (AO LADO) MARACUJA on screen
    And POS QSR-FL-FL clicks on the test_OrderFunctions_MODIFY
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_CHANGESEAT
    And POS QSR-FL-FL selects the filter Sem Assento
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_CHANGESEAT
    And POS QSR-FL-FL selects the filter Assento 1
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 1 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_CHANGESEAT
    And POS QSR-FL-FL selects the filter Assento 2
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 2 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_CHANGESEAT
    And POS QSR-FL-FL selects the filter Assento 3
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 3 on screen
    Then POS QSR-FL-FL clicks on the test_OrderFunctions_CHANGESEAT
    And POS QSR-FL-FL selects the filter Assento 4
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL checks if there's element 4 on screen
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 19,90
    And POS QSR-FL-FL checks if order's TAX is equal to 0,00
    And POS QSR-FL-FL checks if order's TIP is equal to 1,99
    And POS QSR-FL-FL checks if order's TOTAL is equal to 21,89
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 21,89
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 21,89
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL

  Scenario: Mobile test all payment options and then cancel order
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL sets quantity to 10
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's SUBTOTAL is 119,00
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if order's TOTAL is 119,00
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 130,90
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    Then POS QSR-FL-FL pays 5 reais in cash
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's DINHEIRO is equal to 5,00
    And POS QSR-FL-FL checks if order's PAID is equal to 5,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 125,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_TableActions_OPTIONS
    Then POS QSR-FL-FL clicks on the test_TableActions_CLEARTENDERS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL clicks on the test_TableActions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    Then POS QSR-FL-FL clicks on the test_OrderTender_APPLY_DISCOUNTS
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 25 reais
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's DISCOUNT is equal to 25,00
    And POS QSR-FL-FL checks if order's TOTAL_AFTER_DISCOUNT is equal to 94,00
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 105,90
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 105,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    Then POS QSR-FL-FL clicks on the test_OrderTender_APPLY_DISCOUNTS
    And POS QSR-FL-FL selects the filter 2 - Porcentagem
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL sets value to 10 percent
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's DISCOUNT is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL_AFTER_DISCOUNT is equal to 107,10
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 119,00
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    Then POS QSR-FL-FL clicks on the test_OrderTender_CLEAN_DISCOUNTS
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 11,90
    And POS QSR-FL-FL checks if order's TOTAL is equal to 130,90
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 130,90
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    Then POS QSR-FL-FL clicks on the test_TableActions_CHANGETIP
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 25 percent
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 29,75
    And POS QSR-FL-FL checks if order's TOTAL is equal to 148,75
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 148,75
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    Then POS QSR-FL-FL clicks on the test_TableActions_CHANGETIP
    And POS QSR-FL-FL selects the filter Valor
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL sets value to 25 reais
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FL-FL checks if order's SUBTOTAL is equal to 119,00
    And POS QSR-FL-FL checks if order's TIP is equal to 25,00
    And POS QSR-FL-FL checks if order's TOTAL is equal to 144,00
    And POS QSR-FL-FL checks if order's PAID is equal to 0,00
    And POS QSR-FL-FL checks if order's CHANGE is equal to 0,00
    And POS QSR-FL-FL checks if order's DUE is equal to 144,00
    And POS QSR-FL-FL clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FL-FL clicks on the test_TableActions_REOPEN
    And POS QSR-FL-FL clicks on the test_TableOrderHeader_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    And user closes POS QSR-FL-FL

  Scenario: Check table details
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And mobile POS QSR-FL-FL selects food category BEBIDAS as CERVEJAS
    And POS QSR-FL-FL adds BUDWEISER to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORETABLEORDER
    And POS QSR-FL-FL clicks on the test_TableList_OPEN-TABLE
    And POS QSR-FL-FL clicks on the test_TableOrderHeader_RIGHT
    And POS QSR-FL-FL waits 1 seconds
    And mobile POS QSR-FL-FL checks if 1 BUDWEISER is ordered
    And POS QSR-FL-FL clicks on the test_TableOrderHeader_DOWN
    And POS QSR-FL-FL clicks on the test_TableDetailsRenderer_RIGHT
    And mobile POS QSR-FL-FL checks if table's Status is Aberta
    And mobile POS QSR-FL-FL checks if table's Setor is Restaurante
    And mobile POS QSR-FL-FL checks if table's Operador is 1000 / 1000
    And mobile POS QSR-FL-FL checks if table's Nº de pedidos is 1
    And mobile POS QSR-FL-FL checks if table's Subtotal is R$ 11,90
    And mobile POS QSR-FL-FL checks if table's Assentos is 1
    And mobile POS QSR-FL-FL checks if table's TM is R$ 11,90
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Confirma recebimento em Dinheiro: R$ 13,09
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL checks if dialog text is Troco: R$ 0,00
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FL-FL
