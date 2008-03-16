class Rule:
    def __init__(self, context, source):
        self.context = context
        self.source = source

    def evaluate(self):
        return self.source.evaluate()
