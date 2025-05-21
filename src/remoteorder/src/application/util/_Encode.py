# -*- coding: utf-8 -*-
import json

from application.model import RemoteOrderModelJsonEncoder


def get_encoded_json(ex, cls=RemoteOrderModelJsonEncoder):
    # type: (object, Optional[Type[JSONEncoder]]) -> str
    return json.dumps(ex, encoding="utf-8", cls=cls)
