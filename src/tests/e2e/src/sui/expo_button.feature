Feature: EXPO BUTTON

  Background: Reset Skim
    When user opens POS QSR-FL-FL in desktop
    Then POS QSR-FL-FL checks if needs to open day
    Then POS QSR-FL-FL checks if needs to change to PANEL tab
    Then POS QSR-FL-FL checks if the operator needs to logout
    Then POS QSR-FL-FL checks if needs to change to OPERATOR tab
    And POS QSR-FL-FL waits 1 seconds
    Then POS QSR-FL-FL authenticate the operator 1000 login
    And user closes POS QSR-FL-FL

  Scenario: Switch Page and Navigate
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS EXPO waits 3 seconds
    And KDS EXPO sets zoom to 2x2
    And KDS EXPO checks if zoom is 2x2
    And KDS EXPO sends bump command numpad_6
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command numpad_6
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command numpad_6
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command right_arrow
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command right_arrow
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command numpad_-
    And POS EXPO waits 1 seconds
    And KDS EXPO serves all orders
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: KDS Refresh and Undo
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order is 1 CAESAR REGULAR
    And KDS EXPO checks if food is 1 CAESAR REGULAR
    And KDS EXPO checks if side dish is 1 M CAESAR
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command enter
    And POS EXPO waits 3 seconds
    And KDS EXPO sends bump command numpad_7
    And POS EXPO waits 1 seconds
    And KDS EXPO checks if order is 1 CAESAR REGULAR
    And KDS EXPO checks if food is 1 CAESAR REGULAR
    And KDS EXPO checks if side dish is 1 M CAESAR
    And POS EXPO waits 1 seconds
    And KDS EXPO sends bump command enter
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

  Scenario: KDS Zoom
    When user opens POS QSR-FL-FL in desktop
    When user opens EXPO
    And POS QSR-FL-FL clicks on the test_Header_ORDER
    And POS QSR-FL-FL clicks on the test_SubMenu_PRATOS
    And POS QSR-FL-FL adds CAESAR REGULAR and pay
    Then KDS EXPO sets zoom to 2x2
    And POS EXPO waits 0.3 seconds
    And KDS EXPO checks if zoom is 2x2
    And KDS EXPO sends bump command numpad_+
    And POS EXPO waits 0.3 seconds
    And KDS EXPO checks if zoom is 3x3
    And KDS EXPO sends bump command z
    And POS EXPO waits 0.3 seconds
    And KDS EXPO checks if zoom is 4x4
    And KDS EXPO sends bump command numpad_+
    And POS EXPO waits 0.3 seconds
    And KDS EXPO checks if zoom is 5x5
    And KDS EXPO sends bump command enter
    Then user closes POS QSR-FL-FL
    Then user closes POS EXPO

