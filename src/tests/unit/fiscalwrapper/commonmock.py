import mock

from nfce import NfceRequest
from requests import Response


class NfceRequestMaker(object):
    def __init__(self):
        self.status_code = None
        self.content = None
        self.content_list = []
        self.exception = None

    def with_exception(self, exception):
        self.exception = exception
        return self

    def with_content(self, content):
        self.content = content
        return self

    def with_content_list(self, content_list):
        self.content_list = content_list
        return self

    def with_status_code(self, status_code):
        self.status_code = status_code
        return self

    def make(self):
        nfce_request = mock.NonCallableMagicMock(spec=NfceRequest)
        if self.exception is not None:
            nfce_request.envia_nfce = mock.Mock(side_effect=self.exception)
        elif self.content_list:
            response_list = []
            for content in self.content_list:
                response = mock.NonCallableMagicMock(spec=Response)
                response.status_code = 200
                response.content = content
                response_list.append(response)

            nfce_request.envia_nfce = mock.Mock(side_effect=response_list)
        else:
            returned_response = mock.NonCallableMagicMock(spec=Response)
            if self.status_code is not None:
                returned_response.status_code = self.status_code
            else:
                returned_response.status_code = 200

            returned_response.content = self.content
            nfce_request.envia_nfce = mock.Mock(return_value=returned_response)
        return nfce_request
