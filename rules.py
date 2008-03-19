class Rule:
    def __init__(self, context, source, **kwargs):
        self.context = context
        self.source = self.__getSource(source)
        self.args = {}

        # Parse the properties
        for (name, expected_type) in self.source.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                raise TypeError("%s isn't a %s" % (name, expected_type))
            self.args[name] = v

    def __getSource(self, name):
        import sources
        c = getattr(sources, name, None)
        if c and c is not sources.Source and issubclass(c, sources.Source):
            return c()
        raise NameError

    def evaluate(self):
        return self.source.evaluate(self.args)
