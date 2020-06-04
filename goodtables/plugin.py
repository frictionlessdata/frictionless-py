class Plugin:
    def create_check(self, name, *, descriptor=None):
        raise NotImplementedError()

    def create_server(self):
        raise NotImplementedError()
