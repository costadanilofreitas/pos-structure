from _I18n import I18n

from datetime import datetime
import iso8601
from application.repository import I18nRepository

from typing import List  # noqa


class I18nImpl(I18n):
    def __init__(self, i18n_repository):
        # type: (I18nRepository) -> None
        self.i18n_repository = i18n_repository

    def internationalize(self, labels):
        labels_to_translate = self.get_labels_to_translate(labels)
        labels_to_localize = self.get_labels_to_localize(labels)
        translations = self.i18n_repository.internationalize(labels_to_translate)
        localizations = self.localize_labels(labels_to_localize)
        return self.create_internationalized_dict(labels, localizations, translations)

    def internationalize_text(self, text):
        labels = []
        for label in text.split(" "):
            words = self.break_same_words(label)
            labels.extend(words)

        translations = self.internationalize(labels)
        final_text = text
        for word in translations:
            final_text = final_text.replace(word, translations[word])
        return final_text

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
                I18nImpl.add_word_to_translated_labels(word, translated_labels, translations, localizations)
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

        processor = self.processors.get(func_name)
        if processor is None:
            return l10n_func
        else:
            return processor(param_value)

    @staticmethod
    def get_func_name(l10n_function):
        index = l10n_function.index("(")
        return l10n_function[1:index]

    @staticmethod
    def get_param_value(l10n_function):
        index = l10n_function.index("(")
        index2 = l10n_function.index(")")
        return l10n_function[index + 1:index2]

    def process_date_time(self, value):
        return datetime.strftime(iso8601.parse_date(value), self.i18n_repository.get_date_time_format())

    def process_date(self, value):
        return datetime.strftime(iso8601.parse_date(value), self.i18n_repository.get_date_format())

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
        int_value = int(float(value))
        int_part = "{:,d}".format(int_value).replace(",", self.i18n_repository.get_thousands_separator())
        decimal_part = ("{:." + str(self.i18n_repository.get_decimal_places()) + "f}").format(float(value) - int_value) \
                           .replace(".", self.i18n_repository.get_decimal_separator())[1:]
        return int_part + decimal_part
