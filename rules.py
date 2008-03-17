class Rule:
    def __init__(self, context, source, **kwargs):
        self.context = context
        self.source = source
        self.args = {}

        # Parse the properties
        for (name, expected_type) in source.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                raise TypeError("%s isn't a %s" % (name, expected_type))
            self.args[name] = v

    def evaluate(self):
        return self.source.evaluate(self.args)
