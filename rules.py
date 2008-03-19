import gobject

class Rule(gobject.GObject):

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }

    def __init__(self, context, source, **kwargs):
        gobject.GObject.__init__(self)

        self.context = context
        self.source = self.__getSource(source, kwargs)
        self.source.connect("changed", lambda s: self.emit("changed"))
        self.args = {}

        # Parse the properties
        for (name, expected_type) in self.source.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                raise TypeError("%s isn't a %s" % (name, expected_type))
            self.args[name] = v

    def __getSource(self, name, args):
        import sources
        c = getattr(sources, name, None)
        if c and c is not sources.Source and issubclass(c, sources.Source):
            return c(args)
        raise NameError

    def evaluate(self):
        return self.source.evaluate(self.args)

gobject.type_register(Rule)
