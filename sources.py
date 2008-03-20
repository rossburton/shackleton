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


import datetime, dbus, gobject

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

class Source(gobject.GObject):
    # TODO: Marco Polo has the neat ability for sources to suggest values for
    # the properties

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }
    
    def __init__(self, args):
        gobject.GObject.__init__(self)
    
    @staticmethod
    def getProperties():
        """A list of (name, type) pairs."""
        return ()

    def getPollInterval(self):
        # Return the number of seconds between polls if this source should be
        # polled, or 0 if it will fire signals when its evaluation state has
        # changed.
        raise NotImplementedError

    def evaluate(self, args):
        raise NotImplementedError
gobject.type_register(Source)


class TimeSource(Source):

    __instance = None
    def __new__(cls,somearg):
        # Make this a singleton
        if not cls.__instance:
            cls.__instance = super(cls,TimeSource).__new__(cls)
        return cls.__instance

    def __init__(self, args):
        Source.__init__(self, args)

    @staticmethod
    def getProperties():
        return (("time_start", datetime.time), ("time_end", datetime.time))

    def getPollInterval(self):
        # Poll every minute
        return 60

    def evaluate(self, args):
        now = datetime.datetime.now().time()
        return args["time_start"] < now and now < args["time_end"]
gobject.type_register(TimeSource)


class WifiNetworkSource(Source):

    __instance = None
    def __new__(cls,somearg):
        # Make this a singleton
        if not cls.__instance:
            cls.__instance = super(cls,WifiNetworkSource).__new__(cls)
        return cls.__instance

    def __init__(self, args):
        Source.__init__(self, args)
        self.bus = dbus.SystemBus()
        self.nm = self.bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
    
    @staticmethod
    def getProperties():
        return (("ssid", basestring),)
    
    def getPollInterval(self):
        # TODO: return 0 and instead get signals from NM
        return 10
    
    def evaluate(self, args):
        devices = self.nm.getDevices(dbus_interface='org.freedesktop.NetworkManager')
        for path in devices:
            device = self.bus.get_object('org.freedesktop.NetworkManager', path)
            # TODO: I guess this is covered by the props[5] test
            if not device.getLinkActive():
                continue
            
            props = device.getProperties()
            if not props[5]:
                # This device isn't active yet
                continue
            
            if props[2] != 2:
                # Device type is not wireless
                continue
            
            network_path = props[19]
            if not network_path:
                # No active network
                continue
            network = self.bus.get_object('org.freedesktop.NetworkManager', network_path)
            ssid = network.getProperties()[1]
            if ssid == args["ssid"]:
                return True
        return False
gobject.type_register(WifiNetworkSource)


class GConfSource(Source):
    # TODO: have a singleton per GConf key

    def __init__(self, args):
        import gconf, os
        Source.__init__(self, args)
        client = gconf.client_get_default()
        client.add_dir(os.path.dirname(args["key"]), gconf.CLIENT_PRELOAD_NONE)
        client.notify_add(args["key"], self.key_changed)
    
    @staticmethod
    def getProperties():
        return (("key", basestring), ("value", object))
    
    def getPollInterval(self):
        return 0
    
    def key_changed(self, client, id, entry, data):
        self.emit("changed")

    def evaluate(self, args):
        import gconf
        client = gconf.client_get_default()
        try:
            return client.get_value(args["key"]) == args["value"]
        except:
            return False
gobject.type_register(GConfSource)


class BatterySource(Source):

    __instance = None
    def __new__(cls,somearg):
        # Make this a singleton
        if not cls.__instance:
            cls.__instance = super(cls,BatterySource).__new__(cls)
        return cls.__instance

    def __init__(self, args):
        Source.__init__(self, args)
        self.bus = dbus.SessionBus()
        self.pm = self.bus.get_object('org.freedesktop.PowerManagement', '/org/freedesktop/PowerManagement')
        self.pm.connect_to_signal("OnBatteryChanged", self.changed)

    @staticmethod
    def getProperties():
        return (("on_battery", bool),)
    
    def getPollInterval(self):
        return 0
    
    def changed(self, bool):
        # TODO: cache the value and use it when evaluating to avoid DBus calls
        self.emit("changed")
    
    def evaluate(self, args):
        on_battery = self.pm.GetOnBattery()
        return on_battery == args["on_battery"]
gobject.type_register(BatterySource)
