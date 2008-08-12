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

import dbus, dbus.glib
import os, os.path, subprocess


class Action:
    def run(self):
        raise NotImplementedError


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
        subprocess.Popen(self.command, shell=True)

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
        if mode not in ('wallpaper', 'centered', 'scaled', 'zoom'):
            raise KeyError("Invalid mode ('wallpaper', 'centered', 'scaled', 'zoom')")

        self.mode = mode.encode()
        self.image = image.encode()

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
        bus = dbus.SessionBus()
        gossip = bus.get_object("org.gnome.Gossip", "/org/gnome/Gossip")
        if gossip:
            gossip.SetPresence(self.state, self.status)
    
    def __str__(self):
        return "Setting presence"


class HalAction(Action):
    """Abstract action which uses HAL, to avoid boilerplate code."""
    def __init__(self):
        # TODO: put self.hal in class scope so that it is shared
        self.bus = dbus.SystemBus()
        hal_obj = self.bus.get_object('org.freedesktop.Hal', '/org/freedesktop/Hal/Manager')
        self.hal = dbus.Interface(hal_obj, 'org.freedesktop.Hal.Manager')


class BrightnessAction(HalAction):
    def __init__(self, level=100):
        """Level should be between 0 and 100."""
        HalAction.__init__(self)
        self.level = level

    def run(self):
        for udi in self.hal.FindDeviceByCapability('laptop_panel'):
            obj = self.bus.get_object('org.freedesktop.Hal', udi)
            dev = dbus.Interface(obj, 'org.freedesktop.Hal.Device.LaptopPanel')
            dev.SetBrightness(self.level)
    
    def __str__(self):
        return "Setting display brightness to %d" % self.level


class MountAction(Action):
    def __init__(self, mountpoint, mount=True):
        if not os.path.isdir(mountpoint):
            raise KeyError("The mountpoint %s is not a directory" % mountpoint)
        # TODO: add flag to call via gtksudo? use gio or policykit instead?
        self.mountpoint = mountpoint
        self.mount = mount

    def run(self):
        if self.mount:
            # TODO: this test doesn't work for some reason which I discovered
            # before but have now forgotten.
            if not os.path.ismount(self.mountpoint):
                subprocess.check_call(["mount", self.mountpoint])
        else:
            # TODO: this test doesn't work for some reason which I discovered
            # before but have now forgotten.
            if os.path.ismount(self.mountpoint):
                subprocess.check_call(["umount", self.mountpoint])

    def __str__(self):
        if self.mount:
            return "Mounting %s" % self.mountpoint
        else:
            return "Unmounting %s" % self.mountpoint



class DefaultPrinter(Action):
    def __init__(self, name):
        if name is None:
            raise KeyError("No default printer name specified")
        self.name = name
    
    def run(self):
        subprocess.check_call(["lpoptions", "-d", self.name])
    
    def __str__(self):
        return "Setting \"%s\" as the default printer" % self.name
