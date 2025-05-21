from application.model import UpdateType
from application.model.configuration import Configurations
from mbcontextmessagehandler import MbContextMessageBus
from mwhelper import BaseRepository
from persistence import Connection
from typing import Dict


class MediaUpdaterPOSRepository(BaseRepository):

    def __init__(self, message_bus, configs):
        # type: (MbContextMessageBus, Configurations) -> None

        super(MediaUpdaterPOSRepository, self).__init__(message_bus.mbcontext)

        self.message_bus = message_bus
        self.configs = configs
        self.update_type = UpdateType.media
        self.local_configs = configs.updaters[self.update_type.name]

    def get_images_hashes_from_database(self):
        # type: () -> Dict[str: str]
    
        def inner_func(conn):
            # type: (Connection) -> Dict[str: str]
        
            query = "SELECT ProductCode, CustomParamValue FROM ProductCustomParams WHERE CustomParamId = 'ImageHash'"
        
            cursor = conn.select(query)
            
            images_by_hash = dict()
            for row in cursor:
                product_code = row.get_entry("ProductCode")
                guid = row.get_entry("CustomParamValue")
                images_by_hash[product_code] = guid
        
            return images_by_hash
    
        return self.execute_with_connection(inner_func)
