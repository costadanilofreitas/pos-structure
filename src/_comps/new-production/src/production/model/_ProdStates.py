class ProdStates:

    """ class Cmds
    Namespace class for all known production states
    """
    NORMAL = 'NORMAL'        #: Order is in progress
    SERVED = 'SERVED'        #: Order has been assembled
    HELD = 'HELD'            #: Order has stopped being prepared
    READY = 'READY'          #: Order is ready for the customer to pick up
    DELIVERED = 'DELIVERED'  #: Order has been delivered to the customer
    INVALID = 'INVALID'      #: Order is invalid and should be ignored

    # List of all known production order states
    ALL = tuple((name for name in dir() if not name.startswith("_")))
