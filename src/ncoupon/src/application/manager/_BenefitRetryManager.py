from application.interactor import BenefitRetryInteractor
from application.model import BaseThread
from application.model.configuration import Configurations


class BenefitRetryManager(BaseThread):
    def __init__(self, configs, interactor):
        # type: (Configurations, BenefitRetryInteractor) -> None

        super(BenefitRetryManager, self).__init__()
        self.configs = configs
        self.logger = self.configs.logger
        self.interactor = interactor

    def run(self):
        # type: () -> None
        
        while self.running:
            try:
                pending_benefits = self.interactor.get_pending_operations_benefits()
                if not pending_benefits:
                    continue

                benefits_ids = [benefit.benefit_id for benefit in pending_benefits]
                self.logger.info("Found [{}] benefits to retry. Benefits: {}".format(len(benefits_ids), benefits_ids))
                self.interactor.perform_operations_on_pending_benefits(pending_benefits)
            except Exception as _:
                self.logger.exception("Not expected exception")
            finally:
                self.sleep(self.configs.retry_frequency)
