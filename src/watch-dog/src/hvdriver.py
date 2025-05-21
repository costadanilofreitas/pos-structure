from testdoubleutil import SpyCall


class HvDriver(object):
    def restart_component(self, name):
        # type: (str) -> None
        raise NotImplementedError()


class HvDriverSpy(HvDriver):
    def __init__(self):
        self.restart_component_call = SpyCall()

    def restart_component(self, name):
        self.restart_component_call.register_call(name)
