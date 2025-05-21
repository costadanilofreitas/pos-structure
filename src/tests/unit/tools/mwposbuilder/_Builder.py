from abc import ABCMeta, abstractmethod
from typing import List
import os
import shutil


class Builder(object):
    __metaclass__ = ABCMeta

    def __init__(self, source_pos_directory, dest_pos_directory):
        # type: (unicode, unicode) -> None
        self.source_pos_directory = source_pos_directory
        self.dest_pos_directory = dest_pos_directory

    @abstractmethod
    def build(self):
        pass

    def copy_file_list(self, directory, file_list):
        # type: (unicode, List[unicode]) -> None
        source_bin_dir = os.path.join(self.source_pos_directory, directory)
        dest_bin_dir = os.path.join(self.dest_pos_directory, directory)
        for pos_file in file_list:
            shutil.copy(os.path.join(source_bin_dir, pos_file), os.path.join(dest_bin_dir, pos_file))
