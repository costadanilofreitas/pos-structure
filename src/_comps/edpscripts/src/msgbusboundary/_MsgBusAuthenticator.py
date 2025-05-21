from application.domain import Authenticator

from sysactions import authenticate_user, AuthenticationFailed


class MsgBusAuthenticator(Authenticator):
    def authenticate(self, username, password):
        try:
            authenticate_user(username, password)
            return True
        except AuthenticationFailed:
            return False
