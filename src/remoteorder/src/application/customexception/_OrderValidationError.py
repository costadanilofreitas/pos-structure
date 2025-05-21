class OrderValidationError(object):
    OrderWithNoItens = u"OrderWithNoItens"
    InvalidProductPartCode = u"InvalidProductPartCode"
    InvalidPartForParentPartCode = u"InvalidPartForParentPartCode"
    MaxQuantityExceeded = u"MaxQuantityExceeded"
    MinQuantityNotReached = u"MinQuantityNotReached"
    CannotRemoveItemNotInDefault = u"CannotRemoveItemNotInDefault"
    InternalError = u"InternalError"
