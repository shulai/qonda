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

from qonda.mvc.observable import ObservableListProxy


class QueryResult(ObservableListProxy):

    CHUNKSIZE = 20

    def __init__(self, query):
        super(QueryResult, self).__init__([])
        self.__query = query
        self.__len = query.count()

    def __len__(self):
        return self.__len

    def __getitem__(self, i):
        if type(i) == slice:
            if i.stop > self.__len:
                raise IndexError
        try:
            if type(i) == slice:
                if i.stop > len(self._target):
                    raise IndexError
                items = self._target[i]
                if None in items:
                    items = None
            else:
                items = self._target[i]
        except IndexError:
            # Extend list to allocate the required index
            last_index = i if type(i) == int else i.stop - 1
            new_capacity = ((last_index // self.CHUNKSIZE) + 1) * self.CHUNKSIZE
            additional = new_capacity - len(self._target)
            self._target.extend([None] * additional)
            items = None
        if items is None:
            # Read required rows
            if type(i) == int:
                first_index = (i // self.CHUNKSIZE) * self.CHUNKSIZE
                last_index = first_index + self.CHUNKSIZE
            else:
                first_index = (i.start // self.CHUNKSIZE) * self.CHUNKSIZE
                last_index = ((i.stop - 1) // self.CHUNKSIZE + 1
                    ) * self.CHUNKSIZE
            new_items = self.__query[first_index:last_index]
            self._target[first_index:last_index] = new_items
            items = self._target[i]

        return items
