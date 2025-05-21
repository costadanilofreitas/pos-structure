Feature: Mobile Drive Thru Routine

  Background: Reset Skim
    When user opens POS QSR-FL-FL in mobile
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Mobile Payment Options
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And mobile POS QSR-FC-OT sets quantity to 90
    And POS QSR-FC-OT waits 1 seconds
    And POS QSR-FC-OT adds CHOPP COLORADO APPIA 330 ML to order
    And POS QSR-FC-OT waits 1 seconds
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT enters name Fernanda if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in mobile
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_PRINT
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS tests all payment options
    And POS QSR-FL-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-CS waits 1 seconds
    And POS QSR-FC-CS checks if there's option dialog to click yes
    And user closes POS QSR-FC-CS

  Scenario: Mobile Change Customer Name
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT enters name Fernanda if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in mobile
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_PRINT
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_OrderActionsRenderer_COSTUMER-NAME
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS delete text
    And POS QSR-FC-CS send input Camila to keyboard
    And POS QSR-FC-CS clicks on the test_KeyboardDialog_OK
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS checks if dialog text is Confirma recebimento em Dinheiro: R$ 11,90
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-CS

  Scenario: Mobile Customer Doc
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT enters name Fernanda if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in mobile
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_PRINT
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS waits 2 seconds
    And POS QSR-FC-CS clicks on the test_OrderActionsRenderer_COSTUMER-DOC
    And POS QSR-FC-CS waits 2 seconds
    And POS QSR-FC-CS send input 46466603857 to numpad
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_NumPadDialog_OK
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS checks if dialog text is Confirma recebimento em Dinheiro: R$ 11,90
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-CS

  Scenario: Mobile Sell a Product
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT enters name Fernanda if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in mobile
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_PRINT
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-CS

  Scenario: Mobile Recall Options
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT enters name Fernanda if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in mobile
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_PRINT
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_OrderActionsRenderer_SAVE-ORDER
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_RecallScreen_CANCEL
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-CS

  Scenario: OT - Mobile Order Functions (Delete line)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FC-OT clicks on the test_OrderFunctions_DELETELINE
    And POS QSR-FC-OT authenticate as manager
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Order Functions (Delete Last)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT adds MALZEBIER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_DELETELAST
    And POS QSR-FC-OT authenticate as manager
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Order Functions (Quantity)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT waits 0.5 seconds
    And mobile POS QSR-FC-OT checks if order's TOTAL is 11,90
    And mobile POS QSR-FC-OT sets quantity to 0
    And POS QSR-FC-OT adds MALZEBIER to order
    And POS QSR-FC-OT waits 0.5 seconds
    And mobile POS QSR-FC-OT checks if order's TOTAL is 23,80
    And mobile POS QSR-FC-OT sets quantity to 3
    And POS QSR-FC-OT adds BRAHMA ZERO to order
    And POS QSR-FC-OT waits 0.5 seconds
    And mobile POS QSR-FC-OT checks if order's TOTAL is 59,50
    And mobile POS QSR-FC-OT sets quantity to 40
    And POS QSR-FC-OT adds CHOPP BRAHMA 500 ML to order
    And POS QSR-FC-OT waits 0.5 seconds
    And mobile POS QSR-FC-OT checks if order's TOTAL is 778,70
    And mobile POS QSR-FC-OT sets quantity to 50
    And POS QSR-FC-OT adds BOHEMIA PILSEN to order
    And POS QSR-FC-OT waits 0.5 seconds
    And mobile POS QSR-FC-OT checks if order's TOTAL is 1.373,70
    And mobile POS QSR-FC-OT sets quantity to 90
    And POS QSR-FC-OT adds CHOPP COLORADO APPIA 330 ML to order
    And POS QSR-FC-OT waits 0.5 seconds
    And mobile POS QSR-FC-OT checks if order's TOTAL is 2.721,90
    And mobile POS QSR-FC-OT sets quantity to 100
    And POS QSR-FC-OT checks if dialog text is Quantidade máxima de itens excedida
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Order Functions (Options)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT adds MALZEBIER to order
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-OT clicks on the test_OrderFunctions_COMMENT
    And POS QSR-FC-OT send input Não usar copo de vidro to keyboard
    And POS QSR-FC-OT clicks on the test_KeyboardDialog_OK
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Order Functions (Modify)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category SOBREMESAS as CHURROS REGULAR
    And POS QSR-FC-OT waits 1 seconds
    And POS QSR-FC-OT clicks on the test_ItemModifierRenderer_DOCE_DE_LEITE
    And POS QSR-FC-OT clicks on the test_OrderFunctions_MODIFY
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FC-OT clicks on the test_OrderFunctions_MODIFY
    And POS QSR-FC-OT clicks on the test_ItemModifierRenderer_NUTELLA
    And POS QSR-FC-OT clicks on the test_OrderFunctions_MODIFY
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FC-OT checks if there's element NUTELLA on screen
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Order Functions (Cancel)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FL-OT waits 1 seconds
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT selects the filter 1 - Mudou de Ideia
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FC-OT adds BRAHMA ZERO to order
    And POS QSR-FL-OT waits 1 seconds
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT selects the filter 2 - Duplicado
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FC-OT adds CHOPP BRAHMA 500 ML to order
    And POS QSR-FL-OT waits 1 seconds
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT selects the filter 3 - Venda Errada
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FC-OT adds CHOPP BRAHMA 330 ML to order
    And POS QSR-FL-OT waits 1 seconds
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT selects the filter 4 - Cancelamento
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Order Functions (Change Price)
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_UP
    And POS QSR-FC-OT clicks on the test_OrderFunctions_PRICE
    And POS QSR-FC-OT authenticate as manager
    And mobile POS QSR-FC-OT change price to 3,00
    And POS QSR-FC-OT clicks on the test_OrderTotalRenderer_DOWN
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

  Scenario: OT - Mobile Save and Recall Order
    When user opens POS QSR-FC-OT in mobile
    Then POS QSR-FC-OT checks if needs to change to order tab
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT send input Renata to keyboard
    And POS QSR-FC-OT clicks on the test_KeyboardDialog_OK
    And mobile POS QSR-FC-OT selects food category BEBIDAS as CERVEJAS
    And POS QSR-FC-OT adds MALZEBIER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_SAVEORDER
    And POS QSR-FC-OT enters name Fernanda if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And POS QSR-FC-OT clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-OT clicks on the test_OrderFunctions_VOIDORDER
    And POS QSR-FC-OT clicks on the test_FilterableList_OK
    And POS QSR-FC-OT checks if dialog text is Pedido cancelado com sucesso
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And POS QSR-FC-OT clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-OT clicks on the test_OrderPreviewDialog_PRINT
    And POS QSR-FC-OT clicks on the test_RecallScreen_CANCEL
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT



