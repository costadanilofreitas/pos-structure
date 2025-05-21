from production.model.request import ChangePathRequest

from ._ChangePathProcessor import ChangePathProcessor


class DisablePathProcessor(ChangePathProcessor):
    def parse_data(self, data):
        return ChangePathRequest(data, False)
