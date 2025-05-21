from helper import ExtendedEnum


class ListenedEvents(ExtendedEnum):
    EVT_POS_UPDATER_PERFORM_CATALOG_UPDATE = "Evt_PosUpdater_PerformCatalogUpdate"
    EVT_POS_UPDATER_PERFORM_MEDIA_UPDATE = "Evt_PosUpdater_PerformMediaUpdate"
    EVT_POS_UPDATER_PERFORM_USER_UPDATE = "Evt_PosUpdater_PerformUserUpdate"
    EVT_POS_UPDATER_PERFORM_LOADER_UPDATE = "Evt_PosUpdater_PerformLoaderUpdate"
