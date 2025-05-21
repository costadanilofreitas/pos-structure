class ConfigurationReaderException(Exception):
    pass


class NotValidBenefit(Exception):
    pass


class ErrorLockingCoupon(Exception):
    pass


class ErrorUnlockingCoupon(Exception):
    pass


class ErrorBurningCoupon(Exception):
    pass


class ErrorObtainingCouponInfo(Exception):
    pass


class ErrorApplyingBenefit(Exception):
    pass


class BenefitApplierNotFound(Exception):
    pass


class BenefitIdNotFound(Exception):
    pass


class ErrorCheckingVoucher(Exception):
    pass
