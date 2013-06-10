# -*- coding: utf-8 -*-
#
# This file is part of the Qonda framework
# Qonda is (C)2010,2013 Julio César Gázquez
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

from collections import MutableSequence


try:
    from sqlalchemy import orm
except ImportError:
    pass


class Observable(object):
    """
        Base class for observable objects
    """
    def __init__(self):
        self.__dict__['_Observable__callbacks'] = dict()

    try:
        @orm.reconstructor
        def __reconstructor(self):
            self.__callbacks = dict()
    except NameError:
        pass

    def add_callback(self, callback, observer_data=None):
        self.__callbacks[callback] = observer_data

    def remove_callback(self, callback):
        del self.__callbacks[callback]

    def get_callback_data(self, callback):
        return self.__callbacks[callback]

    def set_callback_data(self, callback, data):
        self.__callbacks[callback] = data

    def _notify(self, event_type, event_data=None):
        for k, v in self.__callbacks.iteritems():
            k(self, event_type, v, event_data)


class ObservableObject(Observable):
    """
        Base class for observable objects with automatic property update
        notification

        Inherit and put attribute names into _notifiables to trigger
        notification for theses atributes
    """
    _notifiables = list()

    def __init__(self, notifiables=None):
        Observable.__init__(self)
        if notifiables:
            object.__setattr__(self, '_notifiables', notifiables)

    def __setattr__(self, name, value):
        if name in self._notifiables:
            try:
                getattr(self, name).remove_callback(self._observe_attr)
            except AttributeError:
                pass

        object.__setattr__(self, name, value)
        try:
            if name in self._notifiables:
                self._notify('update', (name,))
                print "observo relacion", getattr(self, name)
                getattr(self, name).add_callback(self._observe_attr, name)
        except AttributeError:
            pass  # If invoked in object construction

    def _observe_attr(self, sender, event_type, my_attr, related_attrs):
        print "_observe_attr", my_attr + '.' + related_attrs
        self._notify('update', my_attr + '.' + related_attrs)


class ReadOnlyProxy(object):
    """
      A proxy class of read only proxies for plain objects.
      Also base class for other proxy classes.
    """
    def __init__(self, target):
        self.__dict__['_target'] = target

    def __getattr__(self, key):
        if key in self.__dict__:
            return self.__dict__[key]
        else:
            return getattr(self.__dict__['_target'], key)


class Proxy(ReadOnlyProxy):
    """
      A class of proxies for plain objects
    """
    def __setattr__(self, key, value):
        if key in self.__dict__:
            self.__dict__[key] = value
        else:
            setattr(self.__dict__['_target'], key, value)


class ObservableProxy(Observable, Proxy):
    """
      A class of proxies for plain objects adding Observer behavior to targets
    """

    _notifiables = list()

    def __init__(self, target, notifiables=None):
        Observable.__init__(self, notifiables)
        Proxy.__init__(self, target)

    def __setattr__(self, name, value):
        Proxy.__set_attr(self, name, value)
        try:
            if name in self._notifiables:
                self._notify('update', (name,))
        except AttributeError:
            pass  # If invoked in object construction


class ObservableListProxy(ReadOnlyProxy, Observable, MutableSequence):

    """
        A class of proxies adding Observer behavior to list targets
        target: target list. Default: None. If None, the proxy creates a new
                target
        target_class: Class for target creation. Default: list
    """

    def __init__(self, target=None, parent=None, target_class=list):
        if target is None:
            target = target_class()
        Observable.__init__(self)
        ReadOnlyProxy.__init__(self, target)
        self.parent = parent

    def __len__(self):
        return len(self.__dict__['_target'])

    def __getitem__(self, i):
        return self._target.__getitem__(i)

    def __setitem__(self, i, x):
        self._notify('before_setitem', i)
        self._target.__setitem__(i, x)
        self._notify('setitem', (i, len(x)))

    def __delitem__(self, i):
        self._notify('before_delitem', i)
        self._target.__delitem__(i)
        self._notify('delitem', i)

    def insert(self, i, x):
        self._notify('before_insert', i)
        self._target.insert(i, x)
        self._notify('insert', i)

    def append(self, x):
        self._notify('before_append')
        self._target.append(x)
        self._notify('append')

    def extend(self, x):
        self._notify('before_extend', len(x))
        self._target.extend(x)
        self._notify('extend', len(x))

    def remove(self, x):
        i = self.index(x)
        del self[i]

    def __repr__(self):
        return self._target.__repr__()
