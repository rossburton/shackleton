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


import config, notify

import gobject, logging
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-d", "--debug", action="store_true", default=False, help="enable debugging")
parser.add_option("-c", "--config", default=None, help="configuration file to read")
(options, args) = parser.parse_args()

if options.debug:
    logging.basicConfig(level=logging.DEBUG)

contexts = config.parse(options.config)

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
poll_interval = reduce (lambda x, y: min(x, y or x), [c.getPollInterval() for c in contexts.itervalues()], 0)
if poll_interval:
    gobject.timeout_add(poll_interval * 1000, poll)

gobject.MainLoop().run()
