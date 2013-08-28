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
from PyQt4.QtCore import Qt
from observable import ObservableObject, ObservableListProxy
from adapters import ObjectAdapter, ObjectListAdapter, ObjectTreeAdapter


class TestObject(ObservableObject):

    _notifiables_ = ('x', 'y', 'z')

    _qonda_column_meta_ = {
        'x': {
            'editFormatter': lambda x: x.upper(),
            'flags': {
                    Qt.ItemIsEnabled: True
                }
            },
        'y': {
            'alignment': Qt.AlignCenter
            },
        'z': { }
        }

    def __init__(self):
        super(TestObject, self).__init__()
        self.x = None
        self.y = None
        self.z = None


class ObjectAdapterTestCase(unittest.TestCase):

    def setUp(self):
        self.model1 = TestObject()
        self.model1.x = u'x1'

        self.model1.y = u'y1'
        self.adapter1 = ObjectAdapter(
            ('x', 'y'),
            self.model1,
            TestObject)
        self.model2 = TestObject()
        self.model2.x = u'x2'

        self.model2.y = u'y2'
        self.adapter2 = ObjectAdapter(
            ('x', 'y'),
            self.model2,
            TestObject)

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
            (self.adapter1, 0, 0, u'x1'),
            (self.adapter1, 0, 1, u'y1'),
            (self.adapter1, 0, 2, None),
            (self.adapter1, 1, 0, None),
            (self.adapter1, -1, 0, None),
            (self.adapter2, 0, 0, u'x2'),
            (self.adapter2, 0, 1, u'y2'),
            (self.adapter2, 0, 2, None))

        for adapter, row, col, value in cases:
            index = adapter.index(row, col)
            adapter_value = adapter.data(index)
            self.assertEqual(adapter_value, value,
                'ObjectAdapter.data on index({0},{1}) failed'.format(row, col))

        for adapter, row, col, value in cases:
            index = adapter.index(row, col)
            adapter_value = adapter.data(index, Qt.EditRole)
            if value is not None and col == 0:
                value = value.upper()
            self.assertEqual(adapter_value, value,
                'ObjectAdapter.data on index({0},{1}) failed'.format(row, col))

        for adapter, row, col, value in cases:
            index = adapter.index(row, col)
            adapter_value = adapter.data(index, Qt.TextAlignmentRole)
            self.assertEqual(adapter_value,
                Qt.AlignCenter if col == 1 else None,
                'ObjectAdapter.data on index({0},{1}) failed'.format(row, col))

    def test_setData(self):

        cases = (
            (self.adapter1, 0, 0, u'a1', True),
            (self.adapter1, 0, 1, u'b1', True),
            (self.adapter1, 0, 2, u'c1', False),
            (self.adapter1, 1, 0, u'd1', False),
            (self.adapter1, -1, 0, u'e1', False),
            (self.adapter2, 0, 0, u'a2', True),
            (self.adapter2, 0, 1, u'b2', True),
            )

        for adapter, row, col, value, expected in cases:
            index = adapter.index(row, col)
            r = adapter.setData(index, value)
            self.assertEqual(r, expected,
                'ObjectAdapter.setData on index({0},{1}) failed'.format(row, col))
            if r:
                adapter_value = adapter.data(index)
                self.assertEqual(adapter_value, value,
                    'ObjectAdapter.setData on index({0},{1}) failed'.format(row, col))

    def test_flags(self):
        cases = (
            (-1, 0, Qt.NoItemFlags),
            (0, -1, Qt.NoItemFlags),
            (0, 2, Qt.NoItemFlags),
            (1, 0, Qt.NoItemFlags),
            (0, 0, Qt.ItemIsEnabled),
            (0, 1, Qt.ItemIsSelectable | Qt.ItemIsEditable
                | Qt.ItemIsEnabled),
            )
        for row, col, expected in cases:
            index = self.adapter1.index(row, col)
            flags = self.adapter1.flags(index)
            self.assertEqual(flags, expected,
                    'ObjectAdapter.flags() on index({0},{1})'.format(row, col))

    # def test_headerData(self):
    # def test_mimeTypes(self):

    def dataChangedSlot(self, topLeft, bottomRight):
        self.dataChangedSignalEmitted = True
        self.dataChangedSlotTop = topLeft.row()
        self.dataChangedSlotLeft = topLeft.column()
        self.dataChangedSlotBottom = bottomRight.row()
        self.dataChangedSlotRight = bottomRight.column()
        self.dataChangedNewValue = topLeft.data()

    def test_model_change(self):
        self.adapter1.dataChanged.connect(self.dataChangedSlot)
        self.dataChangedSignalEmitted = False
        self.model1.x = u'Chuck'
        self.assertTrue(self.dataChangedSignalEmitted,
            "ObjectAdapter didn't emit dataChanged on model change")
        self.assertEqual(
            (self.dataChangedSlotTop, self.dataChangedSlotLeft,
                self.dataChangedSlotBottom, self.dataChangedSlotRight),
            (0, 0, 0, 0), "ObjectAdapter didn't set properly dataChanged"
            " indexes on model change")
        self.assertEqual(self.dataChangedNewValue, u'Chuck',
            "ObjectAdapter retrieved value after model change doesn't match")

        self.dataChangedSignalEmitted = False
        self.model1.y = u'Logistics'
        self.assertTrue(self.dataChangedSignalEmitted,
            "ObjectAdapter didn't emit dataChanged on model change")
        self.assertEqual(
            (self.dataChangedSlotTop, self.dataChangedSlotLeft,
                self.dataChangedSlotBottom, self.dataChangedSlotRight),
            (0, 1, 0, 1), "ObjectAdapter didn't set properly dataChanged"
            " indexes on model change")
        self.assertEqual(self.dataChangedNewValue, u'Logistics',
            "ObjectAdapter retrieved value after model change doesn't match")


class ObjectListAdapterTestCase(unittest.TestCase):

    def setUp(self):

        self.model = ObservableListProxy()
        for i in range(0, 10):
            o = TestObject()
            o.x = 'x{0}'.format(i)
            o.y = 'y{0}'.format(i)
            o.z = 'z{0}'.format(i)
            self.model.append(o)

        self.adapter = ObjectListAdapter(
            ('x', 'y', 'z'),
            self.model,
            TestObject, options=set(['edit']))

    def test_simple(self):
        index = QtCore.QModelIndex()
        self.assertEqual(self.adapter.rowCount(index), 10,
            'ObjectListAdapter.rowCount must return 10')
        self.assertEqual(self.adapter.columnCount(index), 3,
            'ObjectListAdapter.columnCount must return 3')
        index = self.adapter.index(0, 0)
        self.assertEqual(self.adapter.rowCount(index), 0,
            'ObjectListAdapter.rowCount must return 0')
        self.assertEqual(self.adapter.columnCount(index), 0,
            'ObjectListAdapter.columnCount must return 0')

    def test_indexes(self):

        for row in range(-1, 11):
            for col in range(-1, 4):
                index = self.adapter.index(row, col)
                if row in (-1, 10) or col in (-1, 10):
                    self.assertFalse(index.isValid(),
                        ('ObjectListAdapter.index({0},{1})) should be'
                        ' invalid').format(row, col))
                else:
                    self.assertEqual(index.row(), row,
                        'ObjectListAdapter.index({0}, {1}) has wrong row'
                        .format(row, col))
                    self.assertEqual(index.column(), col,
                        'ObjectListAdapter.index({0}, {1}) has wrong column'
                        .format(row, col))

    def test_data(self):
        for row in range(-1, 11):
            for col in range(-1, 4):
                index = self.adapter.index(row, col)
                if row in (-1, 10) or col in (-1, 3):
                    value = None
                else:
                    value = ('x', 'y', 'z')[col] + str(row)
                adapter_value = self.adapter.data(index)
                self.assertEqual(adapter_value, value,
                    'ObjectListAdapter.data on index({0}, {1}) failed'
                        .format(row, col))

        for row in range(-1, 11):
            for col in range(-1, 4):
                index = self.adapter.index(row, col)
                if row in (-1, 10) or col in (-1, 3):
                    value = None
                else:
                    value = ('x', 'y', 'z')[col] + str(row)
                if col == 0 and value is not None:
                    value = value.upper()
                adapter_value = self.adapter.data(index, Qt.EditRole)
                self.assertEqual(adapter_value, value,
                    'ObjectListAdapter.data on index({0}, {1}) failed'
                        .format(row, col))

        for row in range(-1, 11):
            for col in range(-1, 4):
                index = self.adapter.index(row, col)
                if row in (-1, 10) or col in (-1, 3):
                    value = None
                else:
                    value = Qt.AlignCenter if col == 1 else None

                adapter_value = self.adapter.data(index, Qt.TextAlignmentRole)
                self.assertEqual(adapter_value, value,
                    'ObjectListAdapter.data on index({0}, {1}) failed'
                        .format(row, col))

    def test_setData(self):

        for row in range(-1, 11):
            for col in range(-1, 4):
                index = self.adapter.index(row, col)
                value = chr(65 + col) + str(row)
                expected = False if row in (-1, 10) or col in (-1, 3) else True
                r = self.adapter.setData(index, value)
                self.assertEqual(r, expected,
                    ('ObjectListAdapter.setData on index({0}, {1}) failed'
                    'must return {2}')
                    .format(row, col, expected))
                if r:
                    adapter_value = self.adapter.data(index)
                    self.assertEqual(adapter_value, value,
                    'ObjectListAdapter.setData on index({0}, {1}) failed'
                    .format(row, col))

    def test_flags(self):

        for row in range(-1, 11):
            for col in range(-1, 4):            
                index = self.adapter.index(row, col)
                flags = self.adapter.flags(index)
                if row < 0 or row > 9 or col < 0 or col > 2:
                    expected = Qt.NoItemFlags
                elif col == 0:
                    expected = Qt.ItemIsEnabled
                else:
                    expected = (Qt.ItemIsSelectable | Qt.ItemIsEditable 
                        | Qt.ItemIsEnabled)
                self.assertEqual(flags, expected,
                    'ObjectListAdapter.flags() on index {0},{1}'.format(row, col))


# Todo: headerData(), mimeData(), dataChanged signal
# insertRows, removeRows,
# model chabeginInsertRows, insertRows
    # def test_model_flags(self):
    # def test_headerData(self):
    # def test_mimeData(self):
    # def test_model_insertion(self):

    def dataChangedSlot(self, topLeft, bottomRight):
        self.dataChangedSignalEmitted = True
        self.dataChangedSlotTop = topLeft.row()
        self.dataChangedSlotLeft = topLeft.column()
        self.dataChangedSlotBottom = bottomRight.row()
        self.dataChangedSlotRight = bottomRight.column()
        self.dataChangedNewValue = topLeft.data()

    def test_model_change(self):
        self.adapter.dataChanged.connect(self.dataChangedSlot)
        for row in range(-0, 10):
            for attr, col in (('x', 0), ('y', 1), ('z', 2)):
                self.dataChangedSignalEmitted = False
                new_value = '**' + getattr(self.model[row], attr) + '**'
                setattr(self.model[row], attr, new_value)
                self.assertTrue(self.dataChangedSignalEmitted,
                    "ObjectListAdapter didn't emit dataChanged on model change")
                self.assertEqual(
                    (self.dataChangedSlotTop, self.dataChangedSlotLeft,
                        self.dataChangedSlotBottom, self.dataChangedSlotRight),
                    (row, col, row, col),
                    "ObjectListAdapter didn't set properly dataChanged"
                    " indexes on model change")
                self.assertEqual(self.dataChangedNewValue, new_value,
                    "ObjectListAdapter retrieved value after model change"
                    " doesn't match")


    def test_insertRows_deleteRows(self):
        
        values = [[o.x, o.y, o.z] for o in self.model]
        parent = QtCore.QModelIndex()
        self.adapter.insertRows(0, 2, parent)
        self.assertEqual(len(self.model), 12)
        values = [[None] * 3] * 2 + values
        # Should check new rows are different objects?
        for row in range(0, 12):
            self.assertEqual(self.model[row].x, values[row][0])
            self.assertEqual(self.model[row].y, values[row][1])
            self.assertEqual(self.model[row].z, values[row][2])       
        self.adapter.insertRows(12, 3, parent)
        self.assertEqual(len(self.model), 15)
        values = values + [[None] * 3] * 3
        for row in range(0, 15):
            self.assertEqual(self.model[row].x, values[row][0])
            self.assertEqual(self.model[row].y, values[row][1])
            self.assertEqual(self.model[row].z, values[row][2])       

        self.adapter.insertRows(7, 1, parent)
        self.assertEqual(len(self.model), 16)
        values.insert(7, [None] * 3)
        for row in range(0, 16):
            self.assertEqual(self.model[row].x, values[row][0])
            self.assertEqual(self.model[row].y, values[row][1])
            self.assertEqual(self.model[row].z, values[row][2])       

        #deletes
        self.adapter.insertRows(0, 2, parent)
        self.assertEqual(len(self.model), 12)
        values = [[None] * 3] * 2 + values
        # Should check new rows are different objects?
        for row in range(0, 12):
            self.assertEqual(self.model[row].x, values[row][0])
            self.assertEqual(self.model[row].y, values[row][1])
            self.assertEqual(self.model[row].z, values[row][2])       
        self.adapter.insertRows(12, 3, parent)
        self.assertEqual(len(self.model), 15)
        values = values + [[None] * 3] * 3
        for row in range(0, 15):
            self.assertEqual(self.model[row].x, values[row][0])
            self.assertEqual(self.model[row].y, values[row][1])
            self.assertEqual(self.model[row].z, values[row][2])       

        self.adapter.insertRows(7, 1, parent)
        self.assertEqual(len(self.model), 16)
        values.insert(7, [None] * 3)
        for row in range(0, 16):
            self.assertEqual(self.model[row].x, values[row][0])
            self.assertEqual(self.model[row].y, values[row][1])
            self.assertEqual(self.model[row].z, values[row][2])       

class ObjectTreeAdapterTestCase(unittest.TestCase):

    def setUp(self):

        def build_level(level, parent, prefix):
            model = ObservableListProxy()
            for i in range(0, 3):
                o = TestObject()
                o.parent = parent
                o.x = 'x{0}{1}'.format(prefix, i)
                o.y = 'y{0}{1}'.format(prefix, i)
                o.z = 'z{0}{1}'.format(prefix, i)
                o.append(model)
                if level < 3:
                    o.childs = build_level(level + 1, o, prefix + str(i))
            return o

        self.model = build_level(0, None, '')

        self.adapter = ObjectTreeAdapter(
            ('x', 'y', 'z'),
            self.model,
            TestObject, options=set(['edit']))

if __name__ == '__main__':
    unittest.main()
