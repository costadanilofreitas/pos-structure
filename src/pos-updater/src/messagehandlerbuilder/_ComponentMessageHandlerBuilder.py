from threading import Lock

from application.configurator import Configurator
from application.interactor import CatalogUpdaterInteractor, MediaUpdaterInteractor, UserUpdaterInteractor, \
    GetCatalogVersionToApplyInteractor, LoaderUpdaterInteractor
from application.manager import CatalogUpdaterManager, MediaUpdaterManager, UserUpdaterManager, LoaderUpdaterManager
from application.model import ListenedTokens, ListenedEvents, UpdateType, AsyncUuidMessageProcessor, Updater
from application.processor import CatalogUpdaterProcessor, MediaUpdaterProcessor, GetCatalogVersionToApplyProcessor, \
    UserUpdaterProcessor, LoaderUpdaterProcessor
from application.repository.api import CatalogUpdaterAPIRepository, MediaUpdaterAPIRepository, \
    LoaderUpdaterAPIRepository, UserUpdaterAPIRepository
from application.repository.pos import CatalogUpdaterPOSRepository
from application.service import UpdaterService
from application.util import LoggerUtil
from messagehandler import MessageHandlerBuilder
from messageprocessor import MessageProcessorMessageHandler, DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback
from mwhelper import BaseRepository
from typing import Union, Dict, List, Optional

logger = LoggerUtil.get_logger_name(__name__)


class ComponentMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, configurator, pos_repositories):
        # type: (Configurator, List[BaseRepository]) -> None

        self.logger = logger
        self.configs = configurator.configs
        self.pos_repositories = pos_repositories

        self.message_handler = None  # type: Union[None, MessageProcessorMessageHandler]
        self.updaters = {}  # type: Dict[str: Updater]
        self.working_on_update = Lock()

    def build_singletons(self):
        # type: () -> None
        version_to_apply = ListenedTokens.TK_POS_GET_CATALOG_VERSION_TO_APPLY.value

        api_repository = CatalogUpdaterAPIRepository(self.logger, self.configs)
        pos_repository = self.pos_repositories[UpdateType.catalog]
        updater_service = UpdaterService(api_repository, pos_repository, self.working_on_update, self.configs)
        event_processors = {}

        catalog_enabled = self.configs.updaters[UpdateType.catalog.name].enabled
        catalog_interactor = GetCatalogVersionToApplyInteractor(pos_repository, updater_service, catalog_enabled)
        get_catalog_version_to_apply_interactor = catalog_interactor
        msg_processors = {
            version_to_apply: GetCatalogVersionToApplyProcessor(get_catalog_version_to_apply_interactor)
        }

        catalog_updater_processor = self._build_catalog_singletons(pos_repository, updater_service, api_repository)
        media_updater_processor = self._build_media_singletons()
        user_updater_processor = self._build_user_singletons()
        loader_updater_processor = self._build_loader_singletons()
        
        if catalog_updater_processor:
            msg_processors[ListenedTokens.TK_POS_UPDATER_PERFORM_CATALOG_UPDATE.value] = catalog_updater_processor
        if media_updater_processor:
            msg_processors[ListenedTokens.TK_POS_UPDATER_PERFORM_MEDIA_UPDATE.value] = media_updater_processor
            event_processors[ListenedEvents.EVT_POS_UPDATER_PERFORM_MEDIA_UPDATE.value] = media_updater_processor
        if user_updater_processor:
            msg_processors[ListenedTokens.TK_POS_UPDATER_PERFORM_USER_UPDATE.value] = user_updater_processor
            event_processors[ListenedEvents.EVT_POS_UPDATER_PERFORM_USER_UPDATE.value] = user_updater_processor
        if loader_updater_processor:
            msg_processors[ListenedTokens.TK_POS_UPDATER_PERFORM_LOADER_UPDATE.value] = loader_updater_processor
            event_processors[ListenedEvents.EVT_POS_UPDATER_PERFORM_LOADER_UPDATE.value] = loader_updater_processor

        callbacks = [LoggingProcessorCallback(self.logger)]

        self.message_handler = MessageProcessorMessageHandler(event_processors,
                                                              msg_processors,
                                                              None,
                                                              DefaultMessageProcessorExecutorFactory(callbacks),
                                                              logger=self.logger)

        self._start_managers()

    def _start_managers(self):
        for updater in self.updaters:
            if self.updaters[updater].manager:
                self.updaters[updater].manager.start()

    def build_message_handler(self):
        # type: () -> None

        return self.message_handler

    def destroy_singletons(self):
        # type: () -> None

        for updater in self.updaters:
            if self.updaters[updater]:
                self.updaters[updater].manager.stop()

    def destroy_message_handler(self, message_handler):
        # type: (MessageHandlerBuilder) -> None

        return

    def _build_catalog_singletons(self, pos_repo, updater_service, api_repo):
        # type: (CatalogUpdaterPOSRepository, UpdaterService, CatalogUpdaterAPIRepository) -> Optional[CatalogUpdaterProcessor] # noqa

        update_type = UpdateType.catalog
        update_name = update_type.name

        if update_name not in self.configs.updaters:
            return

        local_configs = self.configs.updaters[update_name]
        interactor = CatalogUpdaterInteractor(self.configs, self.working_on_update, api_repo, pos_repo, updater_service,
                                              local_configs.enabled)
        processor = CatalogUpdaterProcessor(interactor)
        manager = CatalogUpdaterManager(self.configs, interactor, api_repo, pos_repo, updater_service)

        local_configs = self.configs.updaters[update_type.name]

        self.updaters[local_configs.name] = Updater(update_type=update_type,
                                                    manager=manager,
                                                    interactor=interactor)

        return processor

    def _build_media_singletons(self):
        # type: () -> Union[AsyncUuidMessageProcessor, None]

        update_type = UpdateType.media
        update_name = update_type.name
        
        if update_name not in self.configs.updaters:
            return
        
        local_configs = self.configs.updaters[update_name]
        api_repo = MediaUpdaterAPIRepository(self.configs)
        pos_repo = self.pos_repositories[UpdateType.media]
        enabled = local_configs.enabled
        interactor = MediaUpdaterInteractor(self.configs, self.working_on_update, api_repo, pos_repo, enabled)
        processor = MediaUpdaterProcessor(interactor)
        manager = MediaUpdaterManager(self.configs, interactor)
        
        self.updaters[local_configs.name] = Updater(update_type=update_type,
                                                    manager=manager,
                                                    interactor=interactor)

        return processor

    def _build_user_singletons(self):
        # type: () -> Union[AsyncUuidMessageProcessor, None]

        update_type = UpdateType.user
        update_name = update_type.name
        
        if update_name not in self.configs.updaters:
            return
        
        local_configs = self.configs.updaters[update_name]
        api_repo = UserUpdaterAPIRepository(self.configs)
        pos_repo = self.pos_repositories[UpdateType.user]
        enabled = local_configs.enabled
        interactor = UserUpdaterInteractor(self.configs, self.working_on_update, api_repo, pos_repo, enabled)
        processor = UserUpdaterProcessor(interactor)
        manager = UserUpdaterManager(self.configs, interactor)
        
        self.updaters[local_configs.name] = Updater(update_type=update_type,
                                                    manager=manager,
                                                    interactor=interactor)

        return processor
    
    def _build_loader_singletons(self):
        # type: () -> Union[AsyncUuidMessageProcessor, None]

        update_type = UpdateType.loader
        update_name = update_type.name
        
        if update_name not in self.configs.updaters:
            return

        api_repo = LoaderUpdaterAPIRepository(logger, self.configs)
        pos_repo = self.pos_repositories[UpdateType.loader]
        updater_service = UpdaterService(api_repo, pos_repo, self.working_on_update, self.configs)
        interactor = LoaderUpdaterInteractor(self.configs, self.working_on_update, api_repo, pos_repo, updater_service)
        processor = LoaderUpdaterProcessor(interactor)
        manager = LoaderUpdaterManager(self.configs, interactor)

        local_configs = self.configs.updaters[update_name]
        self.updaters[local_configs.name] = Updater(update_type, manager, interactor)

        return processor
