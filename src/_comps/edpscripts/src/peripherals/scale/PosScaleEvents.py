from ScaleEvent import ScaleEvent

class PosScaleEvents(object):
    def __init__(self):
        self._wait_pos_id_event_dict = {}
        self._service_name_dict = {}
        self._scale_event_dict = {}

    def create_scale_event(self, pos_id, service_name):
        scale_event = ScaleEvent()
        self._wait_pos_id_event_dict[pos_id] = scale_event
        self._service_name_dict[service_name] = scale_event
        self._scale_event_dict[scale_event] = (pos_id, service_name)

        return scale_event

    def add_weight(self, service_name, weight):
        if service_name not in self._service_name_dict:
            return

        self._service_name_dict[service_name].set_weight(weight)

    def finish_event(self, scale_event):
        pos_id, service_name = self._scale_event_dict[scale_event]

        del self._wait_pos_id_event_dict[pos_id]
        del self._service_name_dict[service_name]
        del self._scale_event_dict[scale_event]


    def get_wait_pos_id_event_dict(self):
        return self._wait_pos_id_event_dict