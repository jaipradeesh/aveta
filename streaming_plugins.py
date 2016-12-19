class Plugin(object):
    name = None
    description = None
    def process(self, frame):
        raise NotImplemented

class Simple(Plugin):
    name = "simple"
    description = "no filters"

    def process(self, frame):
        return frame


plugins = [Simple()]
