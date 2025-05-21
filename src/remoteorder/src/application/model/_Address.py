# -*- coding: utf-8 -*-


class Address(object):
    def __init__(self):
        self.formattedAddress = ""  # type: unicode
        self.streetName = ""        # type: unicode
        self.streetNumber = ""      # type: unicode
        self.complement = ""        # type: unicode
        self.neighborhood = ""      # type: unicode
        self.reference = ""         # type: unicode
        self.city = ""              # type: unicode
        self.state = ""             # type: unicode
        self.postalCode = ""        # type: unicode
        self.country = ""           # type: unicode
        self.latitude = ""          # type: float
        self.longitude = ""         # type: float

