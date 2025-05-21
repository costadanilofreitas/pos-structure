from domain.service import I18nRepository
from sysactions import send_message, get_model
from msgbus import FM_PARAM, TK_I18N_GETMSG, TK_SYS_ACK


class MwI18nRepository(I18nRepository):
    def __init__(self, pos_id):
        self.pos_id = pos_id

        self.lang = self._get_language(pos_id)

        l10n_params = [
            "L10_PYTHON_DATE_FORMAT",
            "L10_PYTHON_DATETIME_FORMAT",
            "L10N_DECIMAL_PLACES",
            "L10N_CURRENCY_DECIMALS",
            "L10N_CURRENCY_SYMBOL",
            "L10N_DECIMALS_SEPARATOR",
            "L10N_THOUSANDS_SEPARATOR",
            "L10N_CURRENCY_SYMBOL_POSITION"
        ]
        l10n_param = self.lang + "\0"
        l10n_param += "\0".join(l10n_params)

        msg = send_message("I18N", TK_I18N_GETMSG, FM_PARAM, l10n_param)
        if msg.token != TK_SYS_ACK:
            raise Exception("Invalid token from I18n: {} - {}".format(msg.token, msg.data))
        l10n_data = self.remove_language_and_last_zero(msg.data)
        self.l10n_params = {}
        count = 0
        for data in l10n_data:
            self.l10n_params[l10n_params[count]] = data
            count += 1

    def get_date_format(self):
        return self.l10n_params["L10_PYTHON_DATE_FORMAT"]

    def get_date_time_format(self):
        return self.l10n_params["L10_PYTHON_DATETIME_FORMAT"]

    def get_decimal_separator(self):
        return self.l10n_params["L10N_DECIMALS_SEPARATOR"]

    def get_thousands_separator(self):
        return self.l10n_params["L10N_THOUSANDS_SEPARATOR"]

    def get_currency_symbol(self):
        return self.l10n_params["L10N_CURRENCY_SYMBOL"]

    def get_currency_symbol_position(self):
        return self.l10n_params["L10N_CURRENCY_SYMBOL_POSITION"]

    def get_decimal_places(self):
        return self.l10n_params["L10N_DECIMAL_PLACES"]

    def internationalize(self, labels):
        dict_words_translated = {}

        param = self.lang + "\0"
        for label in labels:
            if label.startswith("$"):
                param += label[1:] + "\0"
        param = param[:-1]

        msg = send_message("I18N", TK_I18N_GETMSG, FM_PARAM, param)
        if msg.token != TK_SYS_ACK:
            raise Exception("Invalid token from I18N: {} - {}".format(msg.token, msg.data))
        translated_words = self.remove_language_and_last_zero(msg.data)

        count = 0
        for label in labels:
            dict_words_translated[label] = translated_words[count].decode("utf-8")
            count += 1

        return dict_words_translated

    @staticmethod
    def _get_language(pos_id):
        # type: (int) -> str
        model = get_model(pos_id)
        lang = model.findall('Language')[0].get('name')
        return lang

    @staticmethod
    def remove_language_and_last_zero(data):
        return data.split('\0')[1:-1]
