# Copyright (C) 2008 Ross Burton <ross@burtonini.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA 02110-1301 USA


class Action:
    def run(self):
        pass


class DebugAction(Action):
    def __init__(self, message=None):
        self.s = message

    def run(self):
        print self.s

    def __str__(self):
        return "Debug: %s" % self.s


class SpawnAction(Action):
    def __init__(self, command=None):
        self.command = command

    def run(self):
        from subprocess import Popen
        Popen(self.command, shell=True)

    def __str__(self):
        return "Running %s" % self.command.split()[0]


class GConfAction(Action):
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def run(self):
        import gconf
        client = gconf.client_get_default()
        client.set_value(self.key, self.value)

    def __str__(self):
        return "Setting GConf key %s", self.key


class ScreensaverLockAction(GConfAction):
    def __init__(self, locked=True):
        GConfAction.__init__(self, "/apps/gnome-screensaver/lock_enabled", locked)

    def __str__(self):
        if self.value:
            return "Enabling screensaver lock"
        else:
            return "Disabling screensaver lock"


class WallpaperAction(Action):
    def __init__(self, image, mode="zoom"):
        self.image = image.encode()
        # Mode can be 'wallpaper', 'centered', 'scaled', and 'zoom'  
        self.mode = mode.encode()

    def run(self):
        import gconf
        client = gconf.client_get_default()
        client.set_value("/desktop/gnome/background/picture_filename", self.image)
        client.set_value("/desktop/gnome/background/picture_options", self.mode)

    def __str__(self):
        return "Setting Wallpaper"


class GossipStatusAction(Action):
    def __init__(self, state="available", status="Available"):
        if state not in ('available', 'busy', 'away', 'xa'):
            raise KeyError("Invalid state ('available', 'busy', 'away', 'xa')")

        self.state = state
        self.status = status

    def run(self):
        import dbus
        bus = dbus.SessionBus()
        gossip = bus.get_object("org.gnome.Gossip", "/org/gnome/Gossip")
        if gossip:
            gossip.SetPresence(self.state, self.status)
    
    def __str__(self):
        return "Setting presence"
