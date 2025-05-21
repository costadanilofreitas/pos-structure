from _PickListHeaderDto import PickListHeaderDto  # noqa
from _PickListBodyDto import PickListBodyDto  # noqa


class PickListDto(object):
    def __init__(self, pick_list_header, pick_list_body, pod_type, sale_type, pos_id):
        # type: (PickListHeaderDto, PickListBodyDto, unicode, int) -> ()
        self.pick_list_header = pick_list_header
        self.pick_list_body = pick_list_body
        self.pod_type = pod_type
        self.sale_type = sale_type
        self.pos_id = pos_id
