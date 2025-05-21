from application.domain.ui import ScreenChanger
from sysactions import change_screen, get_model


class MsgBusScreenChanger(ScreenChanger):

    def get_main_screen(self, pos_id):
        model = get_model(pos_id)
        return model.find("Screen").get("mainId")

    def change(self, pos_id, screen_id_enum):
        change_screen(pos_id, screen_id_enum.value)

    def change_to_screen_name(self, pos_id, screen_name):
        model = get_model(pos_id)
        screen_id = model.find("Screen").get("mainId")
        change_screen(pos_id, screen_id)
