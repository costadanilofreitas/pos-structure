import sys
import os
import iso8601
from typing import List
from os import listdir
from os.path import isfile, join


class LogLine(object):
    def __init__(self, thread_number, log_date, message, line_content):
        self.thread_number = thread_number
        self.log_date = log_date
        self.message = message
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


def get_message(line_content):
    try:
        index = line_content.index("Thread-")
    except ValueError:
        index = line_content.index("MainThread")
    index2 = line_content.index(" - ", index)
    return line_content[index2 + 3:]


def get_log_date(line_content):
    return iso8601.parse_date(line_content[0:23])


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
                                     get_log_date(first_line),
                                     get_message(line_content),
                                     line_content))
                line_content = ""

            first_line = line
        except:
            pass

        line_content += line + "\n"

    if line_content != "":
        lines.append(LogLine(get_thread_number(first_line),
                             get_log_date(first_line),
                             get_message(line_content),
                             line_content))

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


def get_connection_id(message):
    index = message.index("c_void_p(")
    index2 = message.index(")", index)
    return message[index + 9:index2]


def main():
    log_directory = os.path.abspath(sys.argv[1])
    log_files = [os.path.join(log_directory, f) for f in listdir(log_directory) if isfile(join(log_directory, f)) and ".log" in f]
    log_lines = get_log_lines(read_log_files(log_files))

    separated_lines = separate_lines_by_thread(log_lines)

    opened_connections = {}
    connections_with_transaction = {}
    message_times = {}
    message_max_times = {}
    times = {}
    index = 0
    start_time = None
    message = None
    start_line = None
    for thread_logs in separated_lines:
        for line in thread_logs:
            if line.message.startswith("Opening connection: "):
                opened_connections[get_connection_id(line.message)] = ""
            if line.message.startswith("Closing connection: "):
                connection_id = get_connection_id(line.message)
                if connection_id not in opened_connections:
                    print("Connection {} not opened".format(connection_id))
                else:
                    del opened_connections[connection_id]

            if line.message.startswith("Starting a transaction: "):
                connections_with_transaction[get_connection_id(line.message)] = ""
            if line.message.startswith("Ending a transaction: "):
                connection_id = get_connection_id(line.message)
                if connection_id not in connections_with_transaction:
                    print("Transaction for connection {} not opened".format(connection_id))
                else:
                    del connections_with_transaction[connection_id]

            if line.message.startswith("Handling: "):
                start_time = line.log_date
                start_line = line
                message = line.message[10:].strip()
            if line.message.startswith("Successfully processed: "):
                end_time = line.log_date

                if end_time is not None and start_time is not None:
                    elapsed_time = (end_time - start_time).total_seconds()
                    if elapsed_time > 60:
                        print(start_line)
                    if message not in message_times:
                        message_times[message] = []

                    if message not in message_max_times:
                        message_max_times[message] = elapsed_time
                    elif elapsed_time > message_max_times[message]:
                        message_max_times[message] = elapsed_time
                    message_times[message].append(elapsed_time)

        if len(opened_connections) > 0:
            print("Unclosed connections: {}".format(opened_connections))

        if len(connections_with_transaction) > 0:
            print("Unfinished transactions: {}".format(opened_connections))

        # with open(os.path.join(log_directory, "log{}.log".format(index)), "wb") as log_file:
        #     for line in thread_logs:
        #         log_file.write(line.line_content.encode("utf-8"))
        # index += 1

    for message in message_times:
        times = message_times[message]
        total_time = 0
        for time in times:
            total_time += time

        mean_time = total_time / len(times)

        print("{}: {}".format(message, mean_time))

    print("")

    for message in message_max_times:
        print("{}: {}".format(message, message_max_times[message]))


main()
