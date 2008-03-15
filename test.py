#! /usr/bin/python

from rules import *
import datetime

rules = []
rules.append(AlwaysRule("everywhere"))
rules.append(TimeRule("daytime", time_start=datetime.time(9), time_end=datetime.time(18)))
rules.append(WifiNetworkRule("home", ssid="Burton"))
rules.append(WifiNetworkRule("office", ssid="OH"))

for r in rules:
    print r.getContext(), r.evaluate()
