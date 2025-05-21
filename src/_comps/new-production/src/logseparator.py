import sys
import os
import iso8601
from typing import List
from os import listdir
from os.path import isfile, join


class LogLine(object):
    def __init__(self, thread_number, order_id, line_content):
        self.thread_number = thread_number
        self.order_id = order_id
        self.line_content = line_content


def read_log_files(log_files):
    file_data = ""
    for file_name in log_files:
        with open(file_name, "rb") as f:
            file_data += f.read()

    return file_data.decode("utf-8")


def get_thread_number(line):
    return line.split("-")[4].strip()


def get_order_id(line_content):
    #  type: (str) -> int
    index = line_content.index("\n")
    if index < 0:
        return -1
    index2 = line_content.index("\n", index + 1)
    order_header_line = line_content[index + 1:index2]
    comps = order_header_line.split(",")
    data = comps[0].split(":")
    try:
        return int(data[1].strip())
    except:
        return -1


def get_log_lines(log_data):
    lines = []
    line_content = ""
    first_line = None
    for line in log_data.split('\n'):
        line_start = line[0:23]
        try:
            iso8601.parse_date(line_start)
            if line_content != "":
                lines.append(LogLine(get_thread_number(first_line),
                                     get_order_id(line_content),
                                     line_content))

            first_line = line
            line_content = ""
        except:
            pass

        line_content += line + "\n"

    if line_content != "":
        lines.append(LogLine(get_thread_number(first_line), get_order_id(line_content), line_content))

    return lines


def separate_lines_by_thread(log_lines):
    # type: (List[LogLine]) -> List[List[LogLine]]
    line_dict = {}
    for line in log_lines:
        if line.thread_number not in line_dict:
            line_dict[line.thread_number] = []
        line_dict[line.thread_number].append(line)

    return line_dict.values()


def separate_lines_by_order(log_lines):
    # type: (List[LogLine]) -> List[List[LogLine]]
    line_dict = {}
    for line in log_lines:
        if line.order_id not in line_dict:
            line_dict[line.order_id] = []
        line_dict[line.order_id].append(line)

    return line_dict


def main():
    log_directory = os.path.abspath(sys.argv[1])
    log_files = [os.path.join(log_directory, f) for f in listdir(log_directory) if isfile(join(log_directory, f)) and ".log" in f]
    log_lines = get_log_lines(read_log_files(log_files))

    if len(sys.argv) > 2:
        order_id = int(sys.argv[2])
        lines_by_order = separate_lines_by_order(log_lines)
        if order_id not in lines_by_order:
            print("Order {} not found in files".format(order_id))
            return -1

        order_lines = lines_by_order[order_id]
        with open(os.path.join(log_directory, "{}.log".format(order_id)), "wb") as log_file:
            for line in order_lines:
                log_file.write(line.line_content.encode("utf-8"))
    else:
        separated_lines = separate_lines_by_thread(log_lines)

        index = 0
        for thread_logs in separated_lines:
            with open(os.path.join(log_directory, "log{}.log".format(index)), "wb") as log_file:
                for line in thread_logs:
                    log_file.write(line.line_content.encode("utf-8"))
            index += 1


main()
