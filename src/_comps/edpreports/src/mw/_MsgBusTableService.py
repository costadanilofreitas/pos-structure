import pyscripts
import reports
import sysactions

pyscripts.mbcontext = reports.mbcontext
import tablemgrapi

from domain import TableService

tip_rate = 0


class MsgBusTableService(TableService):

    def get_table_picture(self, pos_id, table_id):
        pyscripts.mbcontext = reports.mbcontext
        sysactions.mbcontext = reports.mbcontext
        tablemgrapi.mbcontext = reports.mbcontext

        model = sysactions.get_model(pos_id)
        posts = tablemgrapi.get_posts(model)
        return posts.getTablePicture(table_id)

    def get_tip_rate(self):
        global tip_rate
        if not tip_rate:
            tip_rate = sysactions.get_storewide_config("Store.TipRate", defval="10")
        return int(tip_rate)
