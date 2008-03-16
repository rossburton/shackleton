#! /usr/bin/python

from rules import *
from context import *
from actions import *
import datetime, time

current_contexts = set()

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
rules.append(TimeRule(contexts["daytime"], time_start=datetime.time(9), time_end=datetime.time(18)))
rules.append(WifiNetworkRule(contexts["office"], ssid="OH"))
rules.append(WifiNetworkRule(contexts["home"], ssid="Burton"))

while True:
    old_contexts = current_contexts.copy()
    current_contexts.clear()
    for r in rules:
        if r.evaluate() and r.getContext() not in current_contexts:
            current_contexts.add(r.getContext())
    
    for c in current_contexts.difference(old_contexts):
        print "Entered", c
        c.runEnteringActions()
    for c in old_contexts.difference(current_contexts):
        print "Left", c
        c.runLeavingActions()
    
    time.sleep(5)

# need some way of marking a default context so for example the screensaver is
# locked when not at home on startup. maybe on first run, execute the leave
# action on any contexts we're not part of?
