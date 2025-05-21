Feature: EXPO


  Background: Reset Skim
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: KUI - Footer order counter
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS EXPO stores footer counter value
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds ORIENTAL REGULAR and pay
    And POS EXPO waits 1 seconds
    And POS EXPO checks if footer counter was increased by 1
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Checks product done with removed item
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds BUFFALO CHICKEN WINGS HALF to order
    And POS QSR-FL-FL clicks the element with text M WINGS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL select order SEM MOLHO
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user opens PREP prep-frito
    And POS prep-frito waits 1 seconds
    And POS prep-frito clicks on the test_ActionsRenderer_DONE
    When user opens EXPO
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order does contains tag DONE
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if kds cell is blinking
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO
    Then user closes POS prep-frito

  Scenario: EXPO - Table TAKE OUT Order
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 2 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SaleType_TAKE-OUT
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS kds-salao waits 1 seconds
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO checks if there's element Mesa on screen
    And POS EXPO waits 1 seconds
    And POS EXPO checks if there's element Viagem on screen
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: EXPO - Consolidate Items Popup (scroll)
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds SUMMER SALAD SIDE to order
    And POS QSR-FL-FL adds ORIENTAL SIDE to order
    And POS QSR-FL-FL adds CAESAR SIDE to order
    And POS QSR-FL-FL adds FRESH HOUSE SIDE to order
    And POS QSR-FL-FL adds SUMMER SALAD REGULAR to order
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL adds FRESH HOUSE REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 1 seconds
    And POS EXPO clicks on the test_FooterRenderer_LIST
    And POS EXPO waits 1 seconds
    And POS EXPO clicks on the test_ScrollPanel_DOWN
    And POS EXPO waits 1 seconds
    And POS EXPO clicks on the test_ScrollPanel_UP
    And POS EXPO waits 1 seconds
    And POS EXPO clicks on the test_ConsolidatedItems_CLOSE
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Order Info
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    Then POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL sets quantity to 5
    And POS QSR-FL-FL adds ORIENTAL REGULAR and pay
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order is 1 CAESAR REGULAR
    And KDS EXPO checks if food is 1 CAESAR REGULAR
    And KDS EXPO checks if side dish is 1 M CAESAR
    And POS EXPO waits 1 seconds
    And KDS EXPO serves the first order
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order is 5 ORIENTAL REGULAR
    And KDS EXPO checks if food is 1 ORIENTAL REGULAR
    And KDS EXPO checks if side dish is 1 M AGRIDOCE
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: SaleType (DL/FC/DT/TT)
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_SaleType_TAKE-OUT
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_SaleType_DRIVE-THRU
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_SaleType_DELIVERY
    And POS QSR-FL-FL adds ARROZ ESPANHOL DL and pay
    And POS QSR-FL-FL clicks on the test_SaleType_EAT-IN
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And KDS EXPO checks if cell 1 saletype is Loja
    And KDS EXPO checks if cell 2 saletype is Viagem
    And KDS EXPO checks if cell 3 saletype is Drive-thru
    And KDS EXPO checks if cell 4 saletype is Delivery
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Consolidated Items List
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL sets quantity to 3
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 3 seconds
    And POS EXPO clicks on the test_FooterRenderer_LIST
    And POS EXPO waits 1 seconds
    And KDS EXPO checks order 5 CAESAR REGULAR on ConsolidatedItemsList
    And POS EXPO waits 1 seconds
    And POS EXPO clicks on the test_ConsolidatedItems_CLOSE
    And POS EXPO waits 3 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Cell Footer
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL stores order id
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 3 seconds
    And KDS EXPO checks if order's operator is 1000
    And KDS EXPO checks cell footer order number
    And POS EXPO waits 3 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Canceled order
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And KDS EXPO checks if there's a canceled order
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Order's Threshold
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO checks thresholds
    And POS QSR-FL-FL waits 2 seconds
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Prep Time - Check Status
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    When user opens PREP prep-chapa
    Then user opens PREP prep-frito
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds INCRÍVEL BURGER to order
    And POS QSR-FL-FL clicks on the test_ProductButton_BATATA-FRITA
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And KDS EXPO checks if order doesnt contains tag DONE
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order does contains tag TIME
    And POS EXPO waits 1 seconds
    And POS prep-chapa clicks on the test_MainScreen_TAB-0
    And POS prep-chapa waits 1 seconds
    And POS prep-chapa clicks on the test_ActionsRenderer_NORMAL
    And POS prep-frito waits 1 seconds
    And POS EXPO waits 3 seconds
    And KDS EXPO checks if order does contains tag DOING
    And KDS EXPO checks if order does contains tag TIME
    And POS EXPO waits 1 seconds
    And POS prep-chapa clicks on the test_MainScreen_TAB-0
    And POS prep-chapa waits 1 seconds
    And POS prep-chapa clicks on the test_ActionsRenderer_DONE
    And POS prep-chapa waits 1 seconds
    And POS prep-chapa clicks on the test_MainScreen_TAB-2
    And POS prep-chapa waits 1 seconds
    And POS prep-chapa checks if there's element INCRÍVEL BURGER on screen
    And POS prep-frito waits 1 seconds
    And POS prep-frito clicks on the test_MainScreen_TAB-0
    And POS prep-frito waits 1 seconds
    And POS prep-frito clicks on the test_ActionsRenderer_NORMAL
    And POS prep-frito waits 1 seconds
    And POS prep-frito clicks on the test_ActionsRenderer_DONE
    And POS prep-frito waits 1 seconds
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order does contains tag DONE
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if kds cell is blinking
    And KDS EXPO serves all orders
    Then user closes POS EXPO
    Then user closes POS QSR-FL-FL
    Then user closes POS prep-chapa
    Then user closes POS prep-frito

  Scenario: Check Course Order
    When user opens POS QSR-FL-FL in desktop
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds FRIES CHILLI QUESO REGULAR to order
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL clicks on the test_SubMenu_SOBREMESAS
    And POS QSR-FL-FL adds CHURROS REGULAR to order
    And POS QSR-FL-FL select order NUTELLA
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL
    Then user opens PREP prep-frito
    And POS prep-frito checks if there's element FRIES CHILLI QUESO REGULAR on screen
    And POS prep-frito waits 2 seconds
    And POS prep-frito clicks on the test_ActionsRenderer_DONE
    When user opens EXPO
    Then KDS EXPO checks if order is 1 FRIES CHILLI QUESO REGULAR
    And KDS EXPO sends bump command enter
    And POS EXPO waits 4 seconds
    And POS prep-frito checks if there's element CAESAR REGULAR on screen
    And POS prep-frito waits 2 seconds
    And POS prep-frito clicks on the test_ActionsRenderer_DONE
    And POS prep-frito waits 2 seconds
    Then KDS EXPO checks if order is 1 CAESAR REGULAR
    And KDS EXPO sends bump command enter
    And POS EXPO waits 10 seconds
    And POS prep-frito checks if there's element CHURROS REGULAR on screen
    And POS prep-frito waits 3 seconds
    And POS prep-frito clicks on the test_ActionsRenderer_DONE
    And POS prep-frito waits 2 seconds
    Then user closes POS prep-frito
    Then KDS EXPO checks if order is 1 CHURROS REGULAR
    And KDS EXPO serves all orders
    Then user closes POS EXPO

  Scenario: Option "Don't make" Order
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds BABY BACK REGULAR 2 ACOMP. to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DONT-MAKE
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then KDS EXPO checks if order is 1 CAESAR REGULAR
    And KDS EXPO serves all orders
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Change order course
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds FRIES CHILLI QUESO REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_CHANGE-COURSE
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    Then KDS EXPO checks if order is 1 FRIES CHILLI QUESO REGULAR
    Then KDS EXPO checks if food is 1 CAESAR REGULAR
    And KDS EXPO serves all orders
    Then user closes POS EXPO
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL

  Scenario: Fire order
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds BABY BACK REGULAR 2 ACOMP. to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_FIRE-ITEM
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds FRIES CHILLI QUESO REGULAR to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then KDS EXPO checks if order is 1 FRIES CHILLI QUESO REGULAR
    Then KDS EXPO checks if order 2 is 1 BABY BACK REGULAR 2 ACOMP.
    And KDS EXPO serves all orders
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Hold order
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 1 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds SUMMER SALAD SIDE to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_HOLD-ITEM
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL SIDE to order    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DONT-MAKE
    And POS QSR-FL-FL adds CAESAR SIDE to order
    And POS EXPO waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order is 1 CAESAR SIDE
    And KDS EXPO serves the first order
    Then user closes POS EXPO
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableItem_TABLE
    And POS QSR-FL-FL clicks on the test_TableOrder_OPTIONS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL select order 1 CAESAR SIDE
    And POS QSR-FL-FL checks if options is disabled
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL select order 1 ORIENTAL SIDE
    And POS QSR-FL-FL checks if options is disabled
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL select order 1 SUMMER SALAD SIDE
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_CLEAR-HOLD-FIRE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    Then user closes POS QSR-FL-FL
    When user opens EXPO
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order is 1 SUMMER SALAD SIDE
    And KDS EXPO serves the first order
    Then user closes POS EXPO
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableItem_TABLE
    And POS QSR-FL-FL clicks on the test_TableActions_DOTOTAL
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    Then user closes POS QSR-FL-FL

  Scenario: Canceled Line subtracting in EXPO
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL clicks on the test_TableStateFilter_AVAILABLE
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL send input 6 to NumPad
    And POS QSR-FL-FL clicks on the test_NumPadDialog_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ADDORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_ENTRADAS
    And POS QSR-FL-FL adds BONELESS BUFFALO WINGS HALF to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds BONELESS BUFFALO WINGS HALF to order
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS EXPO waits 1 seconds
    Then KDS EXPO checks if order is 2 BONELESS BUFFALO WINGS HALF
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if food is 1 M WINGS
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_OPTIONS
    And POS QSR-FL-FL clicks on the test_OrderFunctions_DELETE-LINE
    And POS QSR-FL-FL clicks on the test_OrderFunctions_SAVE-ORDER
    And POS EXPO waits 1 seconds
    Then KDS EXPO checks if order is 1 BONELESS BUFFALO WINGS HALF
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if food is 1 M WINGS
    And KDS EXPO serves all orders
    Then POS QSR-FL-FL checks if needs to change to table tab
    And POS QSR-FL-FL checks if it's in table view
    And POS QSR-FL-FL selects first table
    And POS QSR-FL-FL clicks on the test_TableOrder_CLEAR
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_TableActions_ABANDON
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_YES
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Warning Icon
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL waits 1 seconds
    And POS EXPO checks if icon exclamation is on screen
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS EXPO checks if icon exclamation isn't on screen
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Stored Icon
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_STORE-ORDER
    And POS EXPO checks if icon SaveIcon is on screen
    And POS QSR-FL-FL clicks on the test_Header_RECALL
    And POS QSR-FL-FL clicks on the test_RecallScreen_STORE
    And POS QSR-FL-FL clicks on the test_RecallScreen_CANCEL
    And POS QSR-FL-FL waits 1 seconds
    And POS EXPO checks if icon times is on screen
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Canceled Icon
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderActionsRenderer_BACK-TO-ORDER
    And POS QSR-FL-FL clicks on the test_OrderFunctions_VOID-ORDER
    And POS QSR-FL-FL clicks on the test_FilterableList_OK
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS EXPO checks if icon times is on screen
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: Orders Count
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS EXPO stores order count
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL adds ORIENTAL REGULAR to order
    And POS QSR-FL-FL waits 1 seconds
    And POS QSR-FL-FL clicks on the test_OrderFunctions_TOTAL-ORDER
    And POS QSR-FL-FL skip CPF if needed
    And POS QSR-FL-FL clicks on the test_OrderTender_CASH
    And POS QSR-FL-FL clicks on the test_MessageOptionsDialog_OK
    And POS EXPO checks if order count increases by 2
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO
