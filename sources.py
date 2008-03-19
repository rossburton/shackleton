import datetime, dbus, gobject

# TODO: some sources can be single-instance (wifi), some are better created many
# times (gconf key watcher, one per key).  Some sort of per-class factory method
# is required.  This means changing the Rule API so that sources are constructed
# with their arguments so that the a singleton or new instance can be created as
# required.

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
        return (("ssid", str),)
    
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
        return (("key", str), ("value", object))
    
    def getPollInterval(self):
        return 0
    
    def key_changed(self, client, id, entry, data):
        self.emit("changed")

    def evaluate(self, args):
        import gconf
        client = gconf.client_get_default()
        return client.get_value(args["key"]) == args["value"]
gobject.type_register(GConfSource)
