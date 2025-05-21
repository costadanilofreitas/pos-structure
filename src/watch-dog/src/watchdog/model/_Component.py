from datetime import datetime


class Component(object):
    def __init__(self, name, watch_interval_in_seconds):
        self.name = name
        self.watch_interval_in_seconds = watch_interval_in_seconds
        self.last_run_time = None

    def get_last_run_time(self):
        return self.last_run_time if self.last_run_time else datetime.min

    def set_last_run_time(self, date):
        self.last_run_time = date
