#! /usr/bin/python

# Copyright (C) 2008 Ross Burton <ross@burtonini.com>
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# St, Fifth Floor, Boston, MA 02110-1301 USA


import config
import notify
import gobject
import logging
import sys

from optparse import OptionParser

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

parser = OptionParser()
parser.add_option("-d", "--debug", action="store_true", default=False, help="enable debugging")
parser.add_option("-c", "--config", default=None, help="configuration file to read")
(options, args) = parser.parse_args()

if options.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)

logger = logging.getLogger("shackleton")

try:
    contexts = config.parse(options.config)
except IOError, e:
    logger.warning(str(e))
    sys.exit(1)

current_contexts = set()

for c in contexts.itervalues():
    def changed(context):
        logger.debug("Context %s changed" % context)
        # TODO: wrap in try/except
        if context.evaluateRules():
            if context not in current_contexts:
                current_contexts.add(context)
                notify.enter(context)
                context.runEnteringActions()
        else:
            if context in current_contexts:
                current_contexts.remove(context)
                notify.leave(context)
                context.runLeavingActions()
    c.connect("changed", changed)

# First run needs more magic.  First populate current_contexts with the contexts
# which are active.
for c in contexts.itervalues():
    if c.evaluateRules():
        current_contexts.add(c)

# Now enter all contexts we're in, and leave all contexts we're not in.  It
# might be a good idea to make leaving on startup an option per context.  This
# has to be done in two loops so that we leave before entering.
# TODO: wrap in try/except
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
    logger.debug("Polling for changes")
    reevaluate()
    return True

# Calculate the poll interval
intervals = [c.getPollInterval() for c in contexts.itervalues() if c.getPollInterval()]
if intervals:
    poll_interval = min(intervals)
    logger.debug("Polling for changes every %d seconds" % poll_interval)
    if gobject.timeout_add_seconds:
        gobject.timeout_add_seconds(poll_interval, poll)
    else:
        gobject.timeout_add(poll_interval * 1000, poll)

gobject.MainLoop().run()
