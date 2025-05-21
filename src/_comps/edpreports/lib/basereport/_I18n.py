import iso8601
import unicodedata

from typing import List  # noqa
from datetime import datetime
from dateutil import tz

from ._I18nRepository import I18nRepository


class I18n(object):
    def __init__(self, i18n_repository):
        # type: (I18nRepository) -> None
        self.i18n_repository = i18n_repository

    def internationalize_text(self, text):
        labels = []
        for label in text.split(" "):
            label = unicodedata.normalize('NFKD', unicode(label)).encode('ASCII', 'ignore')
            words = self.break_same_words(label)
            labels.extend(words)

        translations = self.internationalize(labels)
        final_text = text
        for word in translations:
            final_text = final_text.replace(word, translations[word])
        return final_text

    def internationalize(self, labels):
        labels_to_translate = self.get_labels_to_translate(labels)
        labels_to_localize = self.get_labels_to_localize(labels)
        translations = self.i18n_repository.internationalize(labels_to_translate)
        localizations = self.localize_labels(labels_to_localize)
        return self.create_internationalized_dict(labels, localizations, translations)

    def break_same_words(self, label):
        # type: (str) -> List[str]
        index = label.find("$")
        if index < 0:
            return self.break_functions(label)

        first_word = []
        if index > 0:
            first_word = self.break_functions(label[0:index])

        other_word_index = label.find("$", index + 1)
        if other_word_index < 0:
            return first_word + self.break_functions(label[index:])
        else:
            return first_word + self.break_functions(label[index:other_word_index]) + self.break_same_words(
                label[other_word_index:])

    def break_functions(self, label):
        if len(label) == 0:
            return []

        index = label.find("#")
        if index < 0:
            return [label]

        first_word = []
        if index > 0:
            first_word = [label[0:index]]

        other_word_index = label.find(")", index + 1)
        if other_word_index < 0:
            return [label]
        return first_word + [label[index:other_word_index + 1]] + self.break_functions(label[other_word_index + 1:])

    @staticmethod
    def get_labels_to_translate(labels):
        labels_to_translate = []
        for word in labels:
            if word.startswith("$"):
                labels_to_translate.append(word)
        return labels_to_translate

    @staticmethod
    def get_labels_to_localize(labels):
        labels_to_localize = []
        for word in labels:
            if word.startswith("#"):
                labels_to_localize.append(word)
        return labels_to_localize

    def localize_labels(self, labels_to_localize):
        localizations = {}
        l10n_processor = L10nProcessor(self.i18n_repository)
        for label in labels_to_localize:
            localizations[label] = l10n_processor.process_l10n_function(label)
        return localizations

    @staticmethod
    def create_internationalized_dict(labels, localizations, translations):
        translated_labels = {}
        for word in labels:
            if word not in translated_labels:
                I18n.add_word_to_translated_labels(word, translated_labels, translations, localizations)
        return translated_labels

    @staticmethod
    def add_word_to_translated_labels(word, translated_labels, translations, localizations):
        if word in translations:
            translated_labels[word] = translations[word]
        elif word in localizations:
            translated_labels[word] = localizations[word]
        else:
            translated_labels[word] = word


class L10nProcessor(object):
    def __init__(self, i18n_repository):
        # type: (I18nRepository) -> None
        self.i18n_repository = i18n_repository

        self.processors = {
            "DATETIME": self.process_date_time,
            "DATE": self.process_date,
            "CURRENCY_SYMBOL": self.process_currency_symbol,
            "CURRENCY": self.process_currency,
            "NUMBER": self.process_number,
        }

    def process_l10n_function(self, l10n_func):
        func_name = L10nProcessor.get_func_name(l10n_func)
        param_value = L10nProcessor.get_param_value(l10n_func)

        if func_name is None or param_value is None:
            return l10n_func

        processor = self.processors.get(func_name)
        if processor is None:
            return l10n_func
        else:
            return processor(param_value)

    @staticmethod
    def get_func_name(l10n_function):
        index = l10n_function.find("(")
        if index < 0:
            return None
        return l10n_function[1:index]

    @staticmethod
    def get_param_value(l10n_function):
        index = l10n_function.find("(")
        index2 = l10n_function.find(")")
        if index < 0 or index2 < 0:
            return None
        return l10n_function[index + 1:index2]

    def process_date_time(self, value):
        value = iso8601.parse_date(value)
        time_zone = tz.tzlocal()
        return datetime.strftime(value.astimezone(time_zone), self.i18n_repository.get_date_time_format())

    def process_date(self, value):
        value = iso8601.parse_date(value)
        return datetime.strftime(value.astimezone(tzinfo=tz.tzlocal()), self.i18n_repository.get_date_format())

    def process_currency_symbol(self, _):
        return self.i18n_repository.get_currency_symbol()

    def process_currency(self, value):
        currency_symbol_position = self.i18n_repository.get_currency_symbol_position()
        if currency_symbol_position == "after":
            return self.process_number(value) + " " + self.i18n_repository.get_currency_symbol()
        elif currency_symbol_position == "after_no_space":
            return self.process_number(value) + self.i18n_repository.get_currency_symbol()
        elif currency_symbol_position == "before_no_space":
            return self.i18n_repository.get_currency_symbol() + self.process_number(value)
        else:
            return self.i18n_repository.get_currency_symbol() + " " + self.process_number(value)

    def process_number(self, value):
        str_value = ("{:." + str(self.i18n_repository.get_decimal_places()) + "f}").format(float(value))
        return str_value.replace(".", self.i18n_repository.get_decimal_separator())
