class Action:
    def run(self):
        pass

class DebugAction(Action):
    def __init__(self, s):
        self.s = s

    def run(self):
        print self.s
