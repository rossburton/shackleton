#! /usr/bin/python

from rules import *
from context import *
from actions import *
import datetime, time

current_contexts = set()

contexts = {}
c = Context("home")
c.addEnterAction(DebugAction("In Home action"))
contexts["home"] = c
contexts["daytime"] = Context("daytime")
contexts["office"] = Context("office")

rules = []
rules.append(TimeRule(contexts["daytime"], time_start=datetime.time(9), time_end=datetime.time(18)))
rules.append(WifiNetworkRule(contexts["office"], ssid="OH"))
rules.append(WifiNetworkRule(contexts["home"], ssid="Burton"))

while True:
    print "."
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
