from datetime import datetime


class MediaUpdateData(object):
    def __init__(self, product_code=None, image_hash=None, link_to_download=None, expiration_date=None, downloaded=False):
        # type: (str, str, str, datetime, bool) -> None
        
        self.product_code = product_code
        self.image_hash = image_hash
        self.link_to_download = link_to_download
        self.expiration_date = expiration_date
        self.downloaded = downloaded

