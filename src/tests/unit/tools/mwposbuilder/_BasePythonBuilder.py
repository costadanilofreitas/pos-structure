import os
import shutil
from _Builder import Builder


class BasePythonBuilder(Builder):
    def __init__(self, source_pos_directory, dest_pos_directory):
        super(BasePythonBuilder, self).__init__(source_pos_directory, dest_pos_directory)
        
    def build(self):
        shutil.copytree(os.path.join(self.source_pos_directory, "python"), os.path.join(self.dest_pos_directory, "python"))

        file_list = [u"runpackage.py", u"common.pypkg"]
        self.copy_file_list(u"bin", file_list)
