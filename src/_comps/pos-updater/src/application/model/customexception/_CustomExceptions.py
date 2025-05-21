class NoUpdateFound(Exception):
    pass


class ErrorApplyingUpdate(Exception):
    pass


class ConfigurationReaderException(Exception):
    pass


class ErrorInsertingNewUpdateVersion(Exception):
    pass


class ErrorRetrievingPendingUpdate(Exception):
    pass


class ErrorRetrievingUsers(Exception):
    pass


class ErrorCheckingGenesisDir(Exception):
    pass


class ErrorDownloadingUpdatePackage(Exception):
    pass


class ErrorNotifyingAppliedUpdate(Exception):
    pass


class HasNoProductsImagesToDownload(Exception):
    pass


class NotInsideUpdateWindow(Exception):
    pass


class ErrorCheckingPackageIntegrity(Exception):
    pass


class ErrorUpdatingStep(Exception):
    pass


class ErrorUpdatingStatus(Exception):
    pass


class ErrorRestoringBackup(Exception):
    pass


class ErrorCreatingBackup(Exception):
    pass


class NotExpectedException(Exception):
    pass


class ErrorRestartingHV(Exception):
    pass


class DisabledFunctionality(Exception):
    pass


class ErrorDeletingContent(Exception):
    pass


class ErrorExtractingLoaders(Exception):
    pass


class ErrorRecoveringDatabases(Exception):
    pass


class ErrorUpdatingDatabases(Exception):
    pass


class ErrorDownloadingLoaders(Exception):
    pass


class RollbackError(Exception):
    pass
