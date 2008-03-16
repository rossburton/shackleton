import datetime, dbus

class Source:
    # TODO: Marco Polo has the neat ability for sources to suggest values for
    # the properties
    
    def __init__(self, **kwargs):
        # Parse the properties
        for (name, expected_type) in self.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                raise TypeError("%s isn't a %s" % (name, expected_type))
            setattr(self, name, v)

    @staticmethod
    def getProperties():
        """A list of (name, type) pairs."""
        return ()


class TimeSource(Source):
    @staticmethod
    def getProperties():
        return (("time_start", datetime.time), ("time_end", datetime.time))

    def evaluate(self):
        now = datetime.datetime.now().time()
        return self.time_start < now and now < self.time_end


class WifiNetworkSource(Source):
    def __init__(self, **kwargs):
        Source.__init__(self, **kwargs)

        self.bus = dbus.SystemBus()
        self.nm = self.bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
    
    @staticmethod
    def getProperties():
        return (("ssid", str),)
    
    def evaluate(self):
        devices = self.nm.getDevices(dbus_interface='org.freedesktop.NetworkManager')
        for path in devices:
            device = self.bus.get_object('org.freedesktop.NetworkManager', path)
            if device.getLinkActive():
                props = device.getProperties()
                device_type = props[2]
                if device_type != 2: # "Wireless"
                    continue
                # TODO: check that we have an IP, is connected, or something.
                # Otherwise this is true when we're still getting an IP, which
                # isn't good.
                network_path = props[19]
                if not network_path:
                    # No active network
                    continue
                network = self.bus.get_object('org.freedesktop.NetworkManager', network_path)
                ssid = network.getProperties()[1]
                if ssid == self.ssid:
                    return True
        return False
