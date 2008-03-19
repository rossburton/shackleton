#! /usr/bin/python

from actions import *
from context import Context
from rules import Rule
import notify

import datetime, gobject

#import logging
#logging.basicConfig(level=logging.DEBUG)

contexts = {}
rules = []
# TODO: this needs to be read from a configuration file...

c = Context("home")
c.addEnterAction(SpawnAction("zenity --info --text 'Mounting...'"))
c.addLeaveAction(SpawnAction("zenity --info --text 'Unmounting...'"))
c.addEnterAction(ScreensaverLockAction(False))
c.addLeaveAction(ScreensaverLockAction(True))
contexts["home"] = c
contexts["daytime"] = Context("daytime")
contexts["office"] = Context("office")


def getSource(name):
    import sources
    c = getattr(sources, name, None)
    if c and c is not sources.Source and issubclass(c, sources.Source):
        return c()
    return None

rules.append(Rule(contexts["daytime"], getSource("TimeSource"), time_start=datetime.time(9), time_end=datetime.time(18)))
rules.append(Rule(contexts["office"], getSource("WifiNetworkSource"), ssid="OH"))
rules.append(Rule(contexts["home"], getSource("WifiNetworkSource"), ssid="Burton"))

current_contexts = set()

# First run needs more magic.  First populate current_contexts with the contexts
# which are active.
for r in rules:
    if r.evaluate():
        current_contexts.add(r.context)

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


def poll():
    old_contexts = current_contexts.copy()
    current_contexts.clear()
    for r in rules:
        if r.evaluate():
            current_contexts.add(r.context)

    # Run leave before enter
    for c in old_contexts.difference(current_contexts):
        notify.leave(c)
        c.runLeavingActions()
    for c in current_contexts.difference(old_contexts):
        notify.enter(c)
        c.runEnteringActions()
    
    return True

# Calculate the poll interval
poll_interval = reduce (lambda x, y: min(x, y or x), [r.source.getPollInterval() for r in rules])
if poll_interval:
    gobject.timeout_add(poll_interval * 1000, poll)

gobject.MainLoop().run()
