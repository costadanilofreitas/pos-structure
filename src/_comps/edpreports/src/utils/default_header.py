from utils import center, double_line_separator

DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"


def report_default_header(title, pos_id, operator_id, period, current_datetime, store_id=None):
    title = center(title)
    separator = double_line_separator()

    header = separator + "\n"
    header += title + "\n"
    if store_id:
        header += "Loja..........: {}\n".format(store_id.zfill(5)) + "\n"
    header += "Data/hora.....: {}\n".format(current_datetime) + "\n"

    if period is not None:
        fiscal_date = "%02d/%02d/%04d" % (int(period[6:8]), int(period[4:6]), int(period[:4]))
        header += "Data fiscal...: {}".format(fiscal_date) + "\n"

    if operator_id is not None and pos_id is not None:
        header += "ID Operador ..: {} (POS # {})".format(operator_id, pos_id) + "\n"

    header += separator + "\n"

    return header
