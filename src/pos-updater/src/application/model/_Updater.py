from application.interactor import CatalogUpdaterInteractor, MediaUpdaterInteractor, UserUpdaterInteractor
from application.model import BaseThread, UpdateType
from typing import Union


class Updater(object):
    def __init__(self, update_type=None, manager=None, interactor=None):
        # type: (UpdateType, BaseThread, Union[CatalogUpdaterInteractor, MediaUpdaterInteractor, UserUpdaterInteractor]) -> None # noqa

        self.update_type = update_type
        self.manager = manager
        self.interactor = interactor
