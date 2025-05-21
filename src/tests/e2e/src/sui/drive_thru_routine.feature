Feature: Drive Thru Routine

  Scenario: OT|CS - Change Customer Name
    When user opens POS QSR-FC-OT in desktop
    Then POS QSR-FC-OT checks if needs to change to order tab
    And POS QSR-FC-OT clicks on the test_SubMenu_BEBIDAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_STORE-ORDER
    And POS QSR-FC-OT checks if there's option dialog to click ok
    And POS QSR-FC-OT enters name Teste if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in desktop
    And POS QSR-FC-CS waits 1 seconds
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_CLOSE
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_OrderActionsRenderer_COSTUMER-NAME
    And POS QSR-FC-CS delete text
    And POS QSR-FC-CS enters name Teste if needed
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS checks if dialog text is Confirma recebimento em Dinheiro: R$ 11,90
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-CS

  Scenario: OT|CS - Customer Doc
    When user opens POS QSR-FC-OT in desktop
    Then POS QSR-FC-OT checks if needs to change to order tab
    And POS QSR-FC-OT clicks on the test_SubMenu_BEBIDAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_STORE-ORDER
    And POS QSR-FC-OT enters name Teste if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And user closes POS QSR-FC-OT
    When user opens POS QSR-FC-CS in desktop
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_CLOSE
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS clicks on the test_OrderActionsRenderer_COSTUMER-DOC
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS send input 46466603857 to numpad
    And POS QSR-FC-CS waits 1 seconds
    And POS QSR-FC-CS clicks on the test_NumPadDialog_OK
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS checks if dialog text is Confirma recebimento em Dinheiro: R$ 11,90
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-CS

  Scenario: OT|CS - Sell a Product
    When user opens POS QSR-FC-OT in desktop
    Then POS QSR-FC-OT checks if needs to change to order tab
    And POS QSR-FC-OT clicks on the test_SubMenu_BEBIDAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_STORE-ORDER
    And POS QSR-FC-OT enters name Teste if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    When user opens POS QSR-FC-CS in desktop
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_CLOSE
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS clicks on the test_OrderTender_CASH
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT
    And user closes POS QSR-FC-CS

  Scenario: OT|CS - Recall Options
    When user opens POS QSR-FC-OT in desktop
    Then POS QSR-FC-OT checks if needs to change to order tab
    And POS QSR-FC-OT clicks on the test_SubMenu_BEBIDAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_STORE-ORDER
    And POS QSR-FC-OT enters name Teste if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    When user opens POS QSR-FC-CS in desktop
    Then POS QSR-FC-CS checks if needs to change to recall tab
    And POS QSR-FC-CS clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-CS clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-CS clicks on the test_OrderPreviewDialog_CLOSE
    And POS QSR-FC-CS clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-CS clicks on the test_OrderActionsRenderer_SAVE-ORDER
    And POS QSR-FC-CS clicks on the test_RecallScreen_CANCEL
    And POS QSR-FC-CS clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT
    And user closes POS QSR-FC-CS

  Scenario: OT - Save and Recall Order
    When user opens POS QSR-FC-OT in desktop
    Then POS QSR-FC-OT checks if needs to change to order tab
    And POS QSR-FC-OT clicks on the test_SubMenu_BEBIDAS
    And POS QSR-FC-OT adds BUDWEISER to order
    And POS QSR-FC-OT clicks on the test_OrderFunctions_STORE-ORDER
    And POS QSR-FC-OT enters name Teste if needed
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And POS QSR-FC-OT clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-OT clicks on the test_RecallScreen_RECALL
    And POS QSR-FC-OT clicks on the test_OrderFunctions_STORE-ORDER
    And POS QSR-FC-OT clicks on the test_Header_RECALL
    And POS QSR-FC-OT clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-OT clicks on the test_RecallScreen_PREVIEW
    And POS QSR-FC-OT clicks on the test_OrderPreviewDialog_CLOSE
    And POS QSR-FC-OT clicks on the test_RecallScreen_SYNC
    And POS QSR-FC-OT clicks on the test_RecallScreen_CANCEL
    And POS QSR-FC-OT clicks on the test_MessageOptionsDialog_OK
    And user closes POS QSR-FC-OT

