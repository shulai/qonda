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

import unittest
from PyQt4 import QtCore
from observable import ObservableObject
from adapters import ObjectAdapter, ObjectListAdapter


class Employee(ObservableObject):

    _notifiables = ('name', 'section')

    def __init__(self):
        super(Employee, self).__init__()


class ObjectAdapterTestCase(unittest.TestCase):

    def setUp(self):
        self.model1 = Employee()
        self.model1.name = u'John'

        self.model1.section = u'Sales'
        self.adapter1 = ObjectAdapter(
            ('name', 'section'),
            self.model1,
            Employee)
        self.model2 = Employee()
        self.model2.name = u'Bob'
        self.model2.section = u'H.R.'
        self.adapter2 = ObjectAdapter(
            ('name', 'section'),
            self.model2,
            Employee)

    def test_simple(self):
        index = QtCore.QModelIndex()
        self.assertEqual(self.adapter1.rowCount(index), 1,
            'ObjectAdapter.rowCount must return 1')
        self.assertEqual(self.adapter1.columnCount(index), 2,
            'ObjectAdapter.columnCount must return 2')
        index = self.adapter1.index(0, 0)
        self.assertEqual(self.adapter1.rowCount(index), 0,
            'ObjectAdapter.rowCount must return 0')
        self.assertEqual(self.adapter1.columnCount(index), 0,
            'ObjectAdapter.columnCount must return 0')

    def test_indexes(self):

        cases = ((0, 0), (0, 1))

        for case in cases:
            index = self.adapter1.index(*case)
            self.assertEqual(index.row(), case[0],
                'ObjectAdapter.index{0} has wrong row'.format(case))
            self.assertEqual(index.column(), case[1],
                'ObjectAdapter.index{0} has wrong column'.format(case))

        cases = ((0, 2), (1, 0), (-1, 0))
        for case in cases:
            index = self.adapter1.index(*case)
            self.assertFalse(index.isValid(),
            'ObjectAdapter.index{0} should be invalid'.format(case))

    def test_data(self):

        cases = (
            (self.adapter1, (0, 0), u'John'),
            (self.adapter1, (0, 1), u'Sales'),
            (self.adapter1, (0, 2), None),
            (self.adapter1, (1, 0), None),
            (self.adapter1, (-1, 0), None),
            (self.adapter2, (0, 0), u'Bob'),
            (self.adapter2, (0, 1), u'H.R.'),
            (self.adapter2, (0, 2), None))

        for adapter, rowcol, value in cases:
            index = adapter.index(*rowcol)
            adapter_value = adapter.data(index)
            self.assertEqual(adapter_value, value,
                'ObjectAdapter.data on index{0} failed'.format(rowcol))

    def test_setData(self):

        cases = (
            (self.adapter1, (0, 0), u'Rick', True),
            (self.adapter1, (0, 1), u'Engineering', True),
            (self.adapter1, (0, 2), u'Foo', False),
            (self.adapter1, (1, 0), u'Foo', False),
            (self.adapter1, (-1, 0), u'Foo', False),
            (self.adapter2, (0, 0), u'Mike', True),
            (self.adapter2, (0, 1), u'Store', True),
            )

        for adapter, rowcol, value, expected in cases:
            index = adapter.index(*rowcol)
            r = adapter.setData(index, value)
            self.assertEqual(r, expected,
                'ObjectAdapter.setData on index{0} failed'.format(rowcol))
            if r:
                adapter_value = adapter.data(index)
                self.assertEqual(adapter_value, value,
                    'ObjectAdapter.setData on index{0} failed'.format(rowcol))


if __name__ == '__main__':
    unittest.main()
