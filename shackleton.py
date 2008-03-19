#! /usr/bin/python

from actions import *
from context import Context
from rules import Rule
import notify

import datetime, gobject

#import logging
#logging.basicConfig(level=logging.DEBUG)

contexts = {}
# TODO: this needs to be read from a configuration file...

c = Context("home")
c.addRule(Rule("WifiNetworkSource", ssid="Burton"))
c.addEnterAction(DebugAction("Mounting..."))
c.addLeaveAction(DebugAction("Unmounting..."))
c.addEnterAction(ScreensaverLockAction(False))
c.addLeaveAction(ScreensaverLockAction(True))
contexts["home"] = c

contexts["daytime"] = Context("daytime")
contexts["daytime"].addRule(Rule("TimeSource", time_start=datetime.time(9), time_end=datetime.time(18)))

contexts["office"] = Context("office")
contexts["office"].addRule(Rule("WifiNetworkSource", ssid="OH"))

contexts["keyset"] = Context("keyset")
contexts["keyset"].addRule(Rule("GConfSource", key="/apps/dates_window_maximized", value=True))

contexts["daytime-at-office"] = Context("daytime-at-office")
contexts["daytime-at-office"].addRule(Rule("TimeSource", time_start=datetime.time(9), time_end=datetime.time(18)))
contexts["daytime-at-office"].addRule(Rule("WifiNetworkSource", ssid="OH"))

contexts["on-the-go"] = Context("on-the-go")
contexts["on-the-go"].addRule(Rule("BatterySource", on_battery=True))
contexts["on-the-go"].addEnterAction(DebugAction("On the go!"))
contexts["on-the-go"].addLeaveAction(DebugAction("Plugged!"))


current_contexts = set()

for c in contexts.itervalues():
    def changed(c):
        # TODO: instead of reevaluating everything, just re-run this rule
        reevaluate()
    c.connect("changed", changed)

# First run needs more magic.  First populate current_contexts with the contexts
# which are active.
for c in contexts.itervalues():
    if c.evaluateRules():
        current_contexts.add(c)

# Now enter all contexts we're in, and leave all contexts we're not in.  It
# might be a good idea to make leaving on startup an option per context.  This
# has to be done in two loops so that we leave before entering.
for c in contexts.itervalues():
    if c not in current_contexts:
        c.runLeavingActions()
for c in contexts.itervalues():
    if c in current_contexts:
        notify.enter(c)
        c.runEnteringActions()


def reevaluate():
    old_contexts = current_contexts.copy()
    current_contexts.clear()
    for c in contexts.itervalues():
        if c.evaluateRules():
            current_contexts.add(c)
    
    # Run leave before enter
    for c in old_contexts.difference(current_contexts):
        notify.leave(c)
        c.runLeavingActions()
    for c in current_contexts.difference(old_contexts):
        notify.enter(c)
        c.runEnteringActions()

def poll():
    reevaluate()
    return True

# Calculate the poll interval
poll_interval = reduce (lambda x, y: min(x, y or x), [c.getPollInterval() for c in contexts.itervalues()])
if poll_interval:
    gobject.timeout_add(poll_interval * 1000, poll)

gobject.MainLoop().run()
