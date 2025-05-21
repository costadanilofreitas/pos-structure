# -*- coding: utf-8 -*-
# Module name: sysdefs.py
# Module Description: Python module that contains system constants
#
# Copyright © 2010 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

"""
Module sysdefs
Contains system constants
"""


class eft_commands:

    """
    EFT commands
    Aliases: eft, eft_cmds
    """
    EFT_SETMSG = 0x0A01                 # dynamically sets the pinpad msg
    EFT_SETPARAM = 0x0A02               # dynamically sets a driver parameter
    EFT_RESET = 0x0A03                  # resets the pinpad
    EFT_CREDITSALE = 0x0A04             # process a credit EFT payment
    EFT_CREDITSALEREVERSAL = 0x0A05     # process a credit reversal
    EFT_CREDITREFUND = 0x0A06           # performs a credit refund operation
    EFT_CREDITREFUNDREVERSAL = 0x0A07   # performs a credit refund operation
    EFT_DEBITSALE = 0x0A08              # process a debit EFT payment
    EFT_DEBITSALEREVERSAL = 0x0A09      # performs a debit sale reversal
    EFT_CANCELPENDING = 0x0A0A          # cancel a pending operation (cancel operation before the customer swiped the card)
    EFT_GIFTACTIVATE = 0x0A0B           # active a gift card
    EFT_GIFTUNSUBSCRIBE = 0x0A0C        # cancel a gift card subscription
    EFT_GIFTADDVALUE = 0x0A0D           # adds a value into a gift card
    EFT_GIFTREDEEM = 0x0A0E             # process a gift card payment
    EFT_GIFTREFUND = 0x0A0F             # performs a gift refund operation
    EFT_GIFTCASHBACK = 0x0A10           # performs a gift cash-back operation
    EFT_GIFTBALANCE = 0x0A11            # return the current gift card balance (value and points)
    EFT_GIFTMERGE = 0x0A12              # merge contents of 2 gift cards
    EFT_GIFTTRANSFER = 0x0A13           # transfer contents of one gift card to another one
    EFT_GIFTADDPOINTS = 0x0A14          # add points to a gift card
    EFT_GIFTREDEEMPOINTS = 0x0A15       # redeem points from a gift card
    EFT_GIFTADJUST = 0x0A16             # adjust an amout in the gift card
    EFT_REQUESTREPORT = 0x0A17          # request a report from EFT provider
    EFT_CLOSEPERIOD = 0x0A18            # performs a close period in the EFT provider
    EFT_REQUESTSWIPE = 0x0A19           # requests a card swipe from the EFT device
    EFT_ASYNCSALE = 0x0A1A              # start asynchronous EFT payment (either credit or debit)
    EFT_ASYNCCREDITSALE = 0x0A1B        # start asynchronous credit EFT payment
    EFT_ASYNCDEBITSALE = 0x0A1C         # start asynchronous debit EFT payment
    EFT_ASYNCSTEP = 0x0A1D              # continue asynchronous EFT payment
    EFT_ASYNCFINISH = 0x0A1E            # finish asynchronous EFT payment
    EFT_COMMTEST = 0x0A1F               # communication test
    EFT_AUTHORIZE = 0x0A20              # authorize payment
    EFT_DEAUTHORIZE = 0x0A21            # deauthorize payment
    EFT_COMMITAUTHORIZE = 0x0A22        # commit previously authorized payment
    EFT_INIT = 0x0A23                   # commit previously authorized payment


eft = eft_cmds = eft_commands  # Aliases
