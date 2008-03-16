class Action:
    def run(self):
        pass

class DebugAction(Action):
    def __init__(self, s):
        self.s = s

    def run(self):
        print self.s

class SpawnAction(Action):
    def __init__(self, command):
        self.command = command

    def run(self):
        from subprocess import Popen
        Popen(self.command, shell=True)
