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
        self.model1.name = 'John'
        self.model1.section = 'Sales'
        self.adapter1 = ObjectAdapter(
            ('name', 'section'),
            self.model1,
            Employee)
        self.model2 = Employee()
        self.model2.name = 'Bob'
        self.model2.section = 'H.R.'
        self.adapter2 = ObjectAdapter(
            ('name', 'section'),
            self.model2,
            Employee)

    def test_indexes(self):

        index = self.adapter1.index(0, 0)
        self.assertEqual(index.row(), 0,
            'ObjectAdapter.index(0, 0) has wrong row')
        self.assertEqual(index.column(), 0,
            'ObjectAdapter.index(0, 0) has wrong column')

        index = self.adapter1.index(0, 1)
        self.assertEqual(index.row(), 0,
            'ObjectAdapter.index(0, 1) has wrong row')
        self.assertEqual(index.column(), 1,
            'ObjectAdapter.index(0, 1) has wrong column')

        index = self.adapter1.index(0, 2)
        self.assertFalse(index.isValid(),
            'ObjectAdapter.index(0, 2) should be invalid')

        index = self.adapter1.index(1, 0)
        self.assertFalse(index.isValid(),
            'ObjectAdapter.index(1, 0) should be invalid')

    def test_data(self):

        index = self.adapter1.index(0, 0)
        name = self.adapter1.data(index)
        self.assertEqual(name, 'John',
            'ObjectAdapter.data on index(0, 0) failed')

        index = self.adapter1.index(0, 1)
        section = self.adapter1.data(index)
        self.assertEqual(section, 'Sales',
            'ObjectAdapter on index(0, 1) failed')

        index = self.adapter2.index(0, 0)
        name = self.adapter2.data(index)
        self.assertEqual(name, 'Bob',
            'ObjectAdapter.data on index(0, 0) failed')

        index = self.adapter2.index(0, 1)
        section = self.adapter2.data(index)
        self.assertEqual(section, 'H.R.',
            'ObjectAdapter.data on index(0, 1) failed')

if __name__ == '__main__':
    unittest.main()
