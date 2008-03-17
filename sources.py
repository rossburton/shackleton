import datetime, dbus

class Source:
    # TODO: Marco Polo has the neat ability for sources to suggest values for
    # the properties

    @staticmethod
    def getProperties():
        """A list of (name, type) pairs."""
        return ()

    def evaluate(self, args):
        pass


class TimeSource(Source):
    @staticmethod
    def getProperties():
        return (("time_start", datetime.time), ("time_end", datetime.time))

    def evaluate(self, args):
        now = datetime.datetime.now().time()
        return args["time_start"] < now and now < args["time_end"]


class WifiNetworkSource(Source):
    def __init__(self, **kwargs):
        self.bus = dbus.SystemBus()
        self.nm = self.bus.get_object('org.freedesktop.NetworkManager', '/org/freedesktop/NetworkManager')
    
    @staticmethod
    def getProperties():
        return (("ssid", str),)
    
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
