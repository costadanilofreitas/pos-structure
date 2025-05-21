import glob
from datetime import datetime, timedelta
from os import remove, path


class CleanJsonProcessors(object):
    def __init__(self, json_paths, keep_days):
        self.json_paths = json_paths
        self.validation_date = datetime.now() - timedelta(days=keep_days)

    def clean_json(self):
        for json_path in self.json_paths:
            json_files_in_path = glob.glob("{}/*.json".format(json_path))
            for json_file in json_files_in_path:
                if datetime.fromtimestamp(path.getmtime(json_file)) < self.validation_date:
                    remove(json_file)
