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
        cls = self.__getSourceClass(source)

        self.args = {}
        for (name, expected_type) in cls.getProperties():
            v = kwargs[name]
            if not isinstance(v, expected_type):
                # TODO: beat the value into shape if we need to
                raise TypeError("%s isn't a %s" % (name, expected_type))
            self.args[name] = v
        
        self.source = cls(self.args)

    def __getSourceClass(self, name):
        import sources
        c = getattr(sources, name, None)
        if c and c is not sources.Source and issubclass(c, sources.Source):
            return c
        raise NameError, "Cannot find source %s" % name

    def evaluate(self):
        return self.source.evaluate(self.args)
