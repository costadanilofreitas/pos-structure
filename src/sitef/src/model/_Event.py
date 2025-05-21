# encoding: utf-8
class Event(object):
    # Event sent to Totem API to show a box with a keyboard to ask things to the customer
    totemShowKeyboard = "Totem_Show_Keyboard"
    # Event sent to Totem API to show an information box
    totemShowMessageBox = "Totem_Show_MessageBox"
    # Event sent by totem API to the Sitef comp to sent the input textfrom the customer
    # Return of totemShowKeyboard
    totemReturnKeyboard = "Totem_Return_Keyboard"
    # Notify status update of Sitef
    sitefStatusUpdate = "SITEF_STATUS_UPDATE"
