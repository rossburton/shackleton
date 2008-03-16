#! /usr/bin/python

from actions import *
from context import *
from rules import *
from sources import *

import datetime
from time import sleep

contexts = {}
c = Context("home")
c.addEnterAction(SpawnAction("zenity --info --text 'Mounting...'"))
c.addLeaveAction(SpawnAction("zenity --info --text 'Unmounting...'"))
c.addEnterAction(ScreensaverLockAction(False))
c.addLeaveAction(ScreensaverLockAction(True))
contexts["home"] = c
contexts["daytime"] = Context("daytime")
contexts["office"] = Context("office")

rules = []
rules.append(Rule(contexts["daytime"], TimeSource(time_start=datetime.time(9), time_end=datetime.time(18))))
rules.append(Rule(contexts["office"], WifiNetworkSource(ssid="OH")))
rules.append(Rule(contexts["home"], WifiNetworkSource(ssid="Burton")))

current_contexts = set()

# First run needs more magic.  First populate current_contexts with the contexts
# which are active.
for r in rules:
    if r.evaluate():
        current_contexts.add(r.context)

# Now enter all contexts we're in, and leave all contexts we're not in.  It
# might be a good idea to make leaving on startup an option per context.
for c in contexts.itervalues():
    if c in current_contexts:
        c.runEnteringActions()
    else:
        c.runLeavingActions()

# Now loop forever looking for changes
while True:
    sleep(5)
    old_contexts = current_contexts.copy()
    current_contexts.clear()
    for r in rules:
        if r.evaluate():
            current_contexts.add(r.getContext())
    
    for c in current_contexts.difference(old_contexts):
        print "Entered", c
        c.runEnteringActions()
    for c in old_contexts.difference(current_contexts):
        print "Left", c
        c.runLeavingActions()
