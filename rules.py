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


class Rule:
    def __init__(self, source, **kwargs):
        self.source = self.__getSource(source, kwargs)
        self.args = {}

        # Parse the properties
        for (name, expected_type) in self.source.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                raise TypeError("%s isn't a %s" % (name, expected_type))
            self.args[name] = v

    def __getSource(self, name, args):
        import sources
        c = getattr(sources, name, None)
        if c and c is not sources.Source and issubclass(c, sources.Source):
            return c(args)
        raise NameError

    def evaluate(self):
        return self.source.evaluate(self.args)
