# encoding: utf-8
from unicodedata import normalize

from report import Part

COLS = 38
SINGLE_SEPARATOR = ("-" * COLS)
SEPARATOR = ("=" * COLS)
DESCR = 17
DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"


def center(s):
    s = _cut(s)
    miss = COLS - len(s)
    if miss == 0:
        return s
    left = miss / 2
    return (" " * left) + s + "\n"


def join(dic1, dic2):
    d = dict(dic1)
    d.update(dic2)
    return d


def single_line_separator():
    return SINGLE_SEPARATOR + "\n"


def double_line_separator():
    return SEPARATOR + "\n"


def empty_line():
    return " " * COLS + "\n"


def break_line():
    return "\n"


def add_amount_line(descr, qty=None, amount=None, info=None):
    if amount is not None:
        amount = _format_number(float(amount))

    descr = descr[0:DESCR]
    if len(descr) < DESCR:
        descr += '.' * (DESCR - len(descr))

    if qty is not None:
        line = "%s: [%4s] " % (descr, qty)
    else:
        line = "%s: " % descr

    if amount is not None:
        if qty is None:
            line += "       "
        remain = COLS - len(line) - 3
        line += "R$ %*s" % (remain, amount)
    elif info is not None:
        remain = COLS - len(line)
        line += "%*.*s" % (remain, remain, info)

    line += "\n"

    return line


def add_table_line(columns, columns_height, align=None, format_type=None, character_to_add=None):
    index = 0
    lines = ""
    total_columns = len(columns)
    for column in columns:
        current_format_type = 'string' if format_type is None else format_type[index]
        current_align = 'left' if align is None else align[index]
        current_character_to_add = ' ' if character_to_add is None else character_to_add[index]
        current_final_character = ''
        if len(current_character_to_add) > 1:
            current_character_to_add = character_to_add[0][0]
            current_final_character = character_to_add[0][1]

        column = str(column)
        column_len = columns_height[index]

        if current_format_type == 'float':
            formatted_number = '%.2f' % float(column)
            remain = column_len - len(formatted_number)

            line = "{0:<{1:}s}".format(formatted_number, remain) if current_align == 'left' \
                else "{0:>{1:}s}".format(formatted_number, remain)
        elif current_format_type == 'integer':
            line = column[0:column_len]
        else:
            line = column[0:column_len]

        add_characters = column_len - len(_remove_accents(line)) if column_len - len(_remove_accents(line)) > 0 else 0

        if add_characters == 0:
            line = column[0:column_len - 1]
            if index != total_columns - 1:
                lines += line
                if current_final_character != '':
                    line_list = list(lines)
                    line_list[-1] = current_final_character
                    lines = "".join(line_list)

                lines += " "
            else:
                lines += line
        else:
            if current_align == 'right':
                if index != total_columns - 1:
                    lines += (current_character_to_add * (add_characters - 1)) + line + " "
                else:
                    lines += " " + (current_character_to_add * (add_characters - 1)) + line
            else:
                if index != total_columns - 1:
                    lines += line + (current_character_to_add * (add_characters - 1))

                    if current_final_character != '':
                        line_list = list(lines)
                        line_list[-1] = current_final_character
                        lines = "".join(line_list)

                    lines += " "
                else:
                    lines += line + (current_character_to_add * add_characters)

        index += 1

    return lines + "\n"


def add_key_value_line(key, value):
    line = key
    remain = COLS - len(line)
    line += value[0:remain] + "\n"

    if len(value) > remain:
        line += value[remain: (2 * COLS) - remain] + "\n"

    return line


def set_font(font_type):
    font_a = b'\x1b\x4d\x00'
    font_b = b'\x1b\x4d\x01'
    
    if font_type == 'B':
        return [Part(font_b, [])]
    
    return [Part(font_a, [])]


def bold_on():
    return [Part(b'\x1b\x45\x01', [])]


def bold_off():
    return [Part(b'\x1b\x45\x00', [])]


def cut_paper():
    return [Part(b'\x1dV\x01', [])]


def format_cpf_cnpj(value):
    formatted_value = value
    try:
        if len(value) == 11:
            value_to_format = value.zfill(11)
            formatted_value = '{}.{}.{}-{}'.format(value_to_format[:3],
                                                   value_to_format[3:6],
                                                   value_to_format[6:9],
                                                   value_to_format[9:])
        elif len(value) == 14:
            value_to_format = value.zfill(14)
            formatted_value = '{}.{}.{}/{}-{}'.format(value_to_format[:2],
                                                      value_to_format[2:5],
                                                      value_to_format[5:8],
                                                      value_to_format[8:12],
                                                      value_to_format[12:])
    except Exception as _:
        return value
    
    return formatted_value


def _cut(s):
    return s[:COLS] if (len(s) > COLS) else s


def _format_number(number, decimal_places=2, decimal_separator='.', thousand_separator=','):
    sign = '-' if number < 0 else ''
    number = abs(number)
    number, dec = ("%.*f" % (decimal_places, number)).split('.')

    if thousand_separator:
        sepPos = len(number) - 3
        while sepPos >= 1:
            number = number[:sepPos] + thousand_separator + number[sepPos:]
            sepPos -= 3

    if decimal_separator:
        number += (decimal_separator + dec)

    return sign + number


def _remove_accents(text):
    return normalize('NFKD', unicode(text.decode('utf8'))).encode('ascii', 'ignore')
