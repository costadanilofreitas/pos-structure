class Route(object):
    def __init__(self, method, path):
        self.method = method
        self.path = path

    def __eq__(self, o):
        if not isinstance(o, Route):
            return False

        return self.method == o.method and self.path == o.path

    def __ne__(self, o):
        return not self.__eq__(o)

    def __hash__(self):
        return hash((self.method, self.path))

    def __str__(self):
        return "method: {}, path: {}".format(self.method, self.path)

    def __repr__(self):
        return "Route(\"{}\", \"{}\")".format(self.method, self.path)
