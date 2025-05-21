from application.model.customexception import NoUpdateFound, DisabledFunctionality
from application.repository.pos import CatalogUpdaterPOSRepository
from application.service import UpdaterService
from application.util import LoggerUtil

logger = LoggerUtil.get_logger_name(__name__)


class GetCatalogVersionToApplyInteractor:
    def __init__(self, pos_repo, updater_service, enabled):
        # type: (CatalogUpdaterPOSRepository, UpdaterService, bool) -> None
        self.pos_repo = pos_repo
        self.updater_service = updater_service
        self.enabled = enabled

    def get_catalog_version_to_apply(self):
        if not self.enabled:
            raise DisabledFunctionality()
        
        self.updater_service.download_pending_version()
        
        try:
            logger.info("Getting available update version to apply")
            downloaded_version_name = self.pos_repo.get_last_downloaded_version_name()
            if not downloaded_version_name:
                logger.info("No updates available")
                raise NoUpdateFound()
    
            logger.info("Available update version {} to apply".format(downloaded_version_name))
            return downloaded_version_name
        except Exception as _:
            logger.exception("Error getting available update version to apply")
            raise
