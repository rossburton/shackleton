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


import pynotify

pynotify.init("Shackleton")

# TODO
# - add icon
# - set type
# - reduce timeout
# - cache context notifications until they are hidden, so enter/leave is one
#   notification

def enter(context):
    l = ["<b>Entering %s context</b>" % context]
    # TODO: escape the strings
    l += [str(a) for a in context.entering_actions]
    details = "\n\342\200\242 ".join(l)
    n = pynotify.Notification("Changing Context", details)
    n.set_urgency(0)
    n.set_timeout(5 * 1000)
    n.show()

def leave(context):
    l = ["<b>Leaving %s context</b>" % context]
    # TODO: escape the strings
    l += [str(a) for a in context.leaving_actions]
    details = "\n\342\200\242 ".join(l)
    n = pynotify.Notification("Changing Context", details)
    n.set_urgency(0)
    n.set_timeout(5 * 1000)
    n.show()
