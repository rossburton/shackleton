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

class GConfAction(Action):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def run(self):
        import gconf
        client = gconf.client_get_default()
        client.set_value(self.key, self.value)

class ScreensaverLockAction(GConfAction):
    def __init__(self, lock):
        GConfAction.__init__(self, "/apps/gnome-screensaver/lock_enabled", lock)
