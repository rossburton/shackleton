import datetime, dbus

class Rule:
    def __init__(self, context, **kwargs):
        self.context = context;

        for (name, expected_type) in self.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                raise TypeError("%s isn't a %s" % (name, expected_type))
            setattr(self, name, v)

    @staticmethod
    def getProperties():
        """A list of (name, type) pairs."""
        return ()

    def getContext(self):
        return self.context
    
    def getConfidence(self):
        return 1.0

    def evaluate(self):
        pass


class AlwaysRule(Rule):
    def evaluate(self):
        return True


class TimeRule(Rule):
    @staticmethod
    def getProperties():
        return (("time_start", datetime.time), ("time_end", datetime.time))

    def evaluate(self):
        now = datetime.datetime.now().time()
        return self.time_start < now and now < self.time_end


class WifiNetworkRule(Rule):
    def __init__(self, context, **kwargs):
        Rule.__init__(self, context, **kwargs)

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
                if device_type != 2:
                    continue
                
                network_path = props[19]
                network = self.bus.get_object('org.freedesktop.NetworkManager', network_path)
                ssid = network.getProperties()[1]
                if ssid == self.ssid:
                    return True
        return False
