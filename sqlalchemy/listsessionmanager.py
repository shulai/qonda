# -*- coding: utf-8 -*-
#
# This file is part of the Qonda framework
# Qonda is (C)2012,2013 Julio César Gázquez
#
# Qonda is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# any later version.
#
# Qonda is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Qonda; If not, see <http://www.gnu.org/licenses/>.


class ListSessionManager(object):
    """ListSessionManager manages automatic adding of deleting of items
       of an ObservableListProxy into the associated SQLAlchemy session
    """

    def __init__(self, session, target):
        self.__session = session
        self._target = target

    def __call__(self, sender, event_type, list_index, attrs):

        def before_setitem(attrs):
            i, l = attrs
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)

            for i in range(start, stop):
                self.__session.delete(self._target[i])

        def setitem(attrs):
            i, l = attrs
            start = i if type(i) == int else i.start
            stop = start + l
            for i in range(start, stop):
                self.__session.add(self._target[i])

        def before_delitem(i):
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            for i in range(start, stop):
                # See:
                # http://stackoverflow.com/questions/8306506/deleting-an-object-from-an-sqlalchemy-session-before-its-been-persisted
                x = self._target[i]
                if x in self.__session.new:
                    self._session.expunge(x)
                else:
                    self.__session.delete(x)

        def insert(i):
            self.__session.add(self._target[i])

        def append(dummy):
            self.__session.add(self._target[-1])

        def extend(n):
            for i in range(-n, 0):
                self.__session.add(self._target[-1])

        # Call the function named as event_type
        f = locals().get(event_type, None)
        if f is not None:
            f(attrs)
