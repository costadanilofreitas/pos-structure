class ConfigurationReaderException(Exception):
    pass


class InvalidMessageContentException(Exception):
    pass


class PosNotFoundException(Exception):
    pass


class PosotNotFoundException(Exception):
    pass


class OrderNotFoundException(Exception):
    def __init__(self):
        super(Exception, self).__init__("NDISCOUNT_ORDER_NOT_FOUND")


class OrderValidationException(Exception):
    pass


class BenefitNotFound(Exception):
    pass


class BenefitExpiredOrInactiveException(OrderValidationException):
    pass


class PodTypeNotValidException(OrderValidationException):
    pass


class InsufficientSaleAmountException(OrderValidationException):
    pass


class ExcessiveSaleAmountException(OrderValidationException):
    pass


class UserLevelNotAllowedException(OrderValidationException):
    pass


class MissingItemsException(OrderValidationException):
    pass


class CustomBenefitAlreadyAppliedException(OrderValidationException):
    pass


class TimeoutException(Exception):
    def __init__(self):
        super(Exception, self).__init__("NDISCOUNT_TIMEOUT")


class ProductNotFound(Exception):
    def __init__(self):
        super(Exception, self).__init__("NDISCOUNT_PRODUCT_NOT_FOUND")
