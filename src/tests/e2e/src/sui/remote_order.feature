Feature: Remote Order

  Background: The remote order payment types are inserted on database
    When the remote order payment types are inserted on database

  Scenario: Produce json in json_to_test
    When send a order release for json in folder with auto produce off using event method

  Scenario: Produce all jsons on jsons_to_test
    When send a order release for all jsons in folder with auto produce off using event method

  Scenario: Produce all jsons on remote order log
    When send a order release for all jsons in remote order log with limit of 50 orders by log with auto produce off using event method

  Scenario: Void an Remote Order
    When the SacOrderCancel is released to RemoteOrderId: 0a842a93-7ad8-4431-9496-a25fcb69224f
