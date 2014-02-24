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

import copy
from operator import attrgetter


class Aggregator(object):
    """
        Aggregators calculate sum of attributes and item count on lists of
        objects.

        source: list of object
        target: object
        attributes: dict:
            keys = attribute names or '*' for count
            values = list of target attributes
    """
    def __init__(self, source, target, attributes):
        super(Aggregator, self).__init__()
        self.__source = source
        self.__target = target
        self.__attributes = attributes
        self.__values = {}
        self.__new_values = None
        source.add_callback(self.observe)
        count = len(source)
        self.__values['*'] = count

        for attr in attributes.keys():
            if attr == '*':
                continue
            agg_value = 0
            for item in source:
                agg_value += attrgetter(attr)(item)
            self.__values[attr] = agg_value

        for item in source:
            item.add_callback(self.observe_item)
        self.update_target()

    def update_target(self):

        for attr, target_attr in self.__attributes.items():
            setattr(self.__target, target_attr, self.__values[attr])

    def observe(self, sender, event_type, list_row, attrs):

        if sender != self.__source:
            return

        def __before_delitem(i):
            self.__new_values = copy.copy(self.__values)
            item_range = (range(i, i + 1) if type(i) == int
                else range(*(i[0]).indices(len(sender))))
            for attr in self.__attributes.keys():
                if attr == '*':
                    continue
                total = self.__new_values[attr]
                for i in item_range:
                    total -= getattr(sender[i], attr)
                self.__new_values[attr] = total
            self.__new_values['*'] -= len(item_range)
            for i in item_range:
                sender[i].remove_callback(self.observe_item)

        def before_setitem(i):
            __before_delitem(i)

        def setitem(args):
            i, length = args
            item_range = (range(i, i + length) if type(i) == int
                else range(i.start, i.start + length))

            for i in item_range:
                sender[i].add_callback(self.observe_item, i)

            for attr in self.__attributes.keys():
                if attr == '*':
                    continue
                total = self.__new_values[attr]
                for i in item_range:
                    total += getattr(sender[i], attr)
                self.__new_values[attr] = total
            self.__new_values['*'] += length

            self.__values = self.__new_values
            self.update_target()

        def before_delitem(i):
            __before_delitem(i)

        def delitem(i):
            self.__values = self.__new_values
            self.update_target()

        def insert(i):
            sender[i].add_callback(self.observe_item, i)
            for attr in self.__attributes.keys():
                if attr == '*':
                    continue
                try:
                    self.__values[attr] += getattr(sender[i], attr)
                except TypeError:
                    pass  # Probably no value set in the column yet
            self.__values['*'] += 1
            self.update_target()

        def append(dummy):
            insert(len(sender) - 1)

        def extend(length):
            item_range = range(len(sender) - length, len(sender))

            for i in item_range:
                sender[i].add_callback(self.observe_item, i)

            for attr in self.__attributes.keys():
                if attr == '*':
                    continue
                for i in item_range:
                    self.__values[attr] += getattr(sender[i], attr)
            self.__values['*'] += length
            self.update_target()

        # Llamo a la función asociada al event_type
        try:
            locals()[event_type](attrs)
        except KeyError:
            pass

    def observe_item(self, sender, event_type, _, attrs):
        attr = attrs[0]
        if attr in self.__attributes.keys():
            if event_type == 'before_update':
                # self._notify('before_update', 'total')
                self.__values[attr] -= getattr(sender, attr)
            elif event_type == 'update':
                self.__values[attr] += getattr(sender, attr)
                # self._notify('update', 'total')
                self.update_target()