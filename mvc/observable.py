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
from warnings import warn

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
        def reconstructor(self):
            self.__callbacks = dict()
    except NameError:
        pass

    def add_callback(self, callback, observer_data=None):
        """
            Connect a callable to this object.
            The callable will be called when this object emits an event.
            The callable will receive as arguments:
                 The sender object
                 The event type (string)
                 The observer data provided with along the callable in
                 add_callback() or with set_callback_data()
                 The event specific data.
        """
        self.__callbacks[callback] = observer_data

    def remove_callback(self, callback):
        try:
            del self.__callbacks[callback]
        except KeyError:
            warn ("Notice: Call to Observable.remove_callback for no "
                "registered callback")

    def get_callback_data(self, callback):
        return self.__callbacks[callback]

    def set_callback_data(self, callback, data):
        self.__callbacks[callback] = data

    def _notify(self, event_type, event_data=None):
        for callback, observer_data in self.__callbacks.iteritems():
            callback(self, event_type, observer_data, event_data)


class ObservableObject(Observable):
    """
        Base class for observable objects with automatic property update
        notification

        Inherit and put attribute names into _notifiables_ to trigger
        notification for theses atributes.

        Events:
        "before_update": Event data: attribute name
        "update": Event data: attribute name

            Changes in attributes of related Observables also will be
            notified, with the chain of attribute names as a dot separated string
    """
    _notifiables_ = None

    def __init__(self, notifiables=None):
        Observable.__init__(self)
        if notifiables:
            object.__setattr__(self, '_notifiables_', notifiables)

    try:
        @orm.reconstructor
        def reconstructor(self):
            super(ObservableObject, self).reconstructor()
            # Besides creating the callback dict via super()
            # must rebuild the attributes' observation chain
            # as SQLAlchemy doesn't set attributes using __setattr__
            for name, value in vars(self).items():
                try:
                    if value != self:
                        value.add_callback(self._observe_attr, name)
                except AttributeError:
                    pass
    except NameError:
        pass

    def __setattr__(self, name, value):
        if self._notifiables_ is None:
            if name[0] == '_':
                object.__setattr__(self, name, value)
                return
        else:
            if name not in self._notifiables_:
                object.__setattr__(self, name, value)
                return
        try:
            # If new value == old, ignore, hence don't call callbacks
            if getattr(self, name) == value:
                return
        except AttributeError:  # Attribute not assigned yet
            pass

        try:
            getattr(self, name).remove_callback(self._observe_attr)
        except (AttributeError, KeyError):
            # AttributeError: The attribute is new, hence there is no
            # callback to remove
            # KeyError: attributes in SQLAlchemy reconstructed objects
            # don't have callbacks set
            pass

        self._notify('before_update', (name,))
        object.__setattr__(self, name, value)
        try:
            self._notify('update', (name,))
        except AttributeError as e:
              # If invoked in object construction
            print('Notice: AttributeError on update event', str(e))
        try:
            if value != self:  # Avoid circular references
                value.add_callback(self._observe_attr, name)
        except AttributeError as e:
            pass

    def _observe_attr(self, sender, event_type, my_attr, related_attrs):
        if event_type in ('before_update', 'update'):
            self._notify(event_type, [my_attr + '.' + attr
                for attr in related_attrs])


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

    _notifiables_ = list()

    def __init__(self, target, notifiables=None):
        Observable.__init__(self, notifiables)
        Proxy.__init__(self, target)

    def __setattr__(self, name, value):
        Proxy.__set_attr(self, name, value)
        try:
            if name in self._notifiables_:
                self._notify('update', (name,))
        except AttributeError:
            pass  # If invoked in object construction


class ObservableListProxy(ReadOnlyProxy, Observable, MutableSequence):

    """
        A class of proxies adding Observer behavior to list targets
        target: target list. Default: None. If None, the proxy creates a new
                target
        target_class: Class for target creation. Default: list

        Events:
        "before_setitem": Before doing l[i] = x or l[i:j] = new_items
                Event data: index, and replace value length
        "setitem": After doing l[i] = x or l[i:j] = new_items
                Event data: index, and replace value length
        "before_delitem": Before doing del l[i], l.remove(x) or l.pop()
                Event data: index
        "delitem": After doing del l[i], l.remove(x) or l.pop()
                Event data: index
        "before_insert": Before doing l.insert(i, x)
                Event data: index
        "insert": After doing l.insert(i, x)
                Event data: index
        "before_append": Before doing l.append(x)
                Event data: None
        "append": After doing l.append(x)
                Event data: None
        "before_extend": Before doing l.extend(items)
                Event data: len(items)
        "extend": After doing l.extend(items)
                Event data: len(items)
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
        if type(i) == slice:
            i_start = i.start
            i_stop = i.stop
            if i_start is None:
                i_start = 0
            elif i_start < 0:
                i_start = len(self._target) - i_start
            if i_stop is None:
                i_stop = len(self._target)
            elif i_stop < 0:
                i_stop = len(self._target) - i_stop
            i = slice(i_start, i_stop)
            self._notify('before_setitem', (i, len(x)))
            self._target.__setitem__(i, x)
            self._notify('setitem', (i, len(x)))
        else:
            self._notify('before_setitem', (i, 1))
            self._target.__setitem__(i, x)
            self._notify('setitem', (i, 1))

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

    def __eq__(self, other):
        try:
            return self._target == other[:]
        except TypeError:
            return False
