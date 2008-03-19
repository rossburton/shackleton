import datetime, dbus, gobject

cache = {}

# TODO: some sources can be single-instance (wifi), some are better created many
# times (gconf key watcher, one per key).  Some sort of per-class factory method
# is required.  This means changing the Rule API so that sources are constructed
# with their arguments so that the a singleton or new instance can be created as
# required.

def getSource(name):
    global cache

    s = cache.get(name, None)
    if s:
        return s

    c = globals().get(name, None)
    if c and c is not Source and issubclass(c, Source):
        cache[name] = c()
        return cache[name]
    
    return None


class Source(gobject.GObject):
    # TODO: Marco Polo has the neat ability for sources to suggest values for
    # the properties

    __gsignals__ = {
        'changed': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
        }
    
    def __init__(self):
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
    def __init__(self):
        Source.__init__(self)

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
    def __init__(self, **kwargs):
        Source.__init__(self)
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
    def __init__(self):
        Source.__init__(self)

    @staticmethod
    def getProperties():
        return (("key", str), ("value", object))
    
    def getPollInterval(self):
        # TODO: return 0 and instead get key change notifications
        return 10
    
    def evaluate(self, args):
        import gconf
        client = gconf.client_get_default()
        return client.get_value(args["key"]) == args["value"]
gobject.type_register(GConfSource)
