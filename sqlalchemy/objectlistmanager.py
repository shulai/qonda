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


class ObjectListManager(object):
    """ObjectListManager manages changes in an ObservableListProxy,
    for later applying them into an SQLAlchemy session
    """

    def __init__(self, target):
        self._new = set()
        self._dirty = set()
        self._deleted = set()
        self._target = target
        target.add_callback(self._observe_list)
        for item in target:
            item.add_callback(self._observe_target)

    def _observe_list(self, sender, event_type, list_index, attrs):

        def _add_to_target(item):
            if item in self._deleted:
                self._deleted.remove(item)
            else:
                self._new.add(item)

        def _remove_from_target(item):
            if item in self._new:
                self._new.remove(item)
            else:
                self._deleted.add(item)


        def before_setitem(attrs):
            i, l = attrs
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)

            for i in range(start, stop):
                _remove_from_target(self._target[i])

        def setitem(attrs):
            i, l = attrs
            start = i if type(i) == int else i.start
            stop = start + l
            for i in range(start, stop):
                _add_to_target(self._target[i])

        def before_delitem(i):
            start, stop = (i, i + 1) if type(i) == int else (i.start, i.stop)
            for i in range(start, stop):
                _remove_from_target(self._target[i])

        def insert(i):
            _add_to_target(self._target[i])

        def append(dummy):
            _add_to_target(self._target[-1])

        def extend(n):
            for i in range(-n, 0):
                _add_to_target(self._target[i])

        if self._target != sender:
            raise ValueError('Event sender != target')
        # Call the function named as event_type
        f = locals().get(event_type, None)
        if f is not None:
            f(attrs)
    
    def _observe_target(self, sender, event_type, list_index, attrs):
        if sender not in self._new:
            self._dirty.add(sender)

    def apply_to_session(self, session):
        for item in self._dirty - self._deleted:
            session.merge(item)
        session.flush()
        for item in self._deleted:
            session.delete(item)
        session.flush()
        session.add_all(self._new)
        session.flush()
