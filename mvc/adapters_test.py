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
import random
from PyQt4.QtCore import Qt
from observable import ObservableObject, ObservableListProxy
from adapters import (ObjectAdapter, ObjectListAdapter, ObjectTreeAdapter,
    PythonObjectRole)


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
        'z': {}
        }

    def __init__(self):
        super(TestObject, self).__init__()
        self.x = None
        self.y = None
        self.z = None

    def __eq__(self, other):
        if not isinstance(other, TestObject):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __repr__(self):
        return "({0},{1},{2})".format(self.x, self.y, self.z)


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

    def test_rows_columns(self):
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
            o.x = u'x{0}'.format(i)
            o.y = u'y{0}'.format(i)
            o.z = u'z{0}'.format(i)
            self.model.append(o)

        self.adapter = ObjectListAdapter(
            ('x', 'y', 'z'),
            self.model,
            TestObject, options=set(['edit']))

    def test_rows_columns(self):
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
                if row in (-1, 10) or col in (-1, 3):
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
                    value = getattr(self.model[row], ('x', 'y', 'z')[col])
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
                    value = getattr(self.model[row], ('x', 'y', 'z')[col])
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
                    model_value = getattr(self.model[row], ('x', 'y', 'z')[col])
                    self.assertEqual(model_value, value,
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
                    'ObjectListAdapter.flags() on index {0},{1}'
                    .format(row, col))

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

    def test_insertRows(self):

        # Should test on other parent indexes than the invalid index
        model_copy = self.model[:]

        self.adapter.insertRows(0, 2)
        self.adapter.setData(self.adapter.index(0, 0), 31)
        self.adapter.setData(self.adapter.index(1, 2), 37)
        self.assertEqual(len(self.model), 12)
        model_copy = [TestObject(), TestObject()] + model_copy
        model_copy[0].x = 31
        model_copy[1].z = 37
        self.assertEqual(self.model, model_copy)

        self.adapter.insertRows(12, 3)
        self.assertEqual(len(self.model), 15)
        model_copy = model_copy + [TestObject(), TestObject(), TestObject()]
        self.assertEqual(self.model, model_copy)

        self.adapter.insertRows(7, 1)
        self.assertEqual(len(self.model), 16)
        model_copy[7:7] = [TestObject()]
        self.assertEqual(self.model, model_copy)

    def test_deleteRows(self):

        # Should test on other parent indexes than the invalid index
        model_copy = self.model[:]

        self.adapter.removeRows(4, 2)
        self.assertEqual(len(self.model), 8)
        del model_copy[4:6]
        self.assertEqual(self.model, model_copy)

        self.adapter.removeRows(6, 2)
        self.assertEqual(len(self.model), 6)
        del model_copy[6:8]
        self.assertEqual(self.model, model_copy)

        self.adapter.removeRows(0, 4)
        self.assertEqual(len(self.model), 2)
        del model_copy[0:4]
        self.assertEqual(self.model, model_copy)

    def test_insert(self):
        self.model.insert(5, TestObject())
        self.assertEqual(self.adapter.rowCount(), 11)
        for row in range(4, 7):
            for col in range(0, 3):
                index = self.adapter.index(row, col)
                value = getattr(self.model[row], ('x', 'y', 'z')[col])
                adapter_value = self.adapter.data(index, PythonObjectRole)
                self.assertEqual(adapter_value, value,
                    'test_model_insert failed')

    def test_append(self):
        o = TestObject()
        o.y = 4242
        self.model.append(o)
        self.assertEqual(self.adapter.rowCount(), 11)
        for row in range(9, 11):
            for col in range(0, 3):
                index = self.adapter.index(row, col)
                value = getattr(self.model[row], ('x', 'y', 'z')[col])
                adapter_value = self.adapter.data(index, PythonObjectRole)
                self.assertEqual(adapter_value, value,
                    'test_model_append failed')

    def test_extend(self):
        l = [TestObject(), TestObject()]
        l[0].x = 42
        l[1].z = 21
        self.model.extend(l)
        self.assertEqual(self.adapter.rowCount(), 12)
        for row in range(9, 12):
            for col in range(0, 3):
                index = self.adapter.index(row, col)
                value = getattr(self.model[row], ('x', 'y', 'z')[col])
                adapter_value = self.adapter.data(index, PythonObjectRole)
                self.assertEqual(adapter_value, value,
                    'test_model_extend failed')

    def test_model_del(self):
        del self.model[6]
        self.assertEqual(self.adapter.rowCount(), 9)
        for row in range(5, 7):
            for col in range(0, 3):
                index = self.adapter.index(row, col)
                value = getattr(self.model[row], ('x', 'y', 'z')[col])
                adapter_value = self.adapter.data(index, PythonObjectRole)
                self.assertEqual(adapter_value, value,
                    'test_model_insertion failed')
        # Add more deletion cases

    def test_model_setslice(self):
        l = [TestObject(), TestObject()]
        l[0].x = 63
        l[1].z = 67
        self.model[2:8] = l
        self.assertEqual(self.adapter.rowCount(), 6)
        for row in range(0, 6):
            for col in range(0, 3):
                index = self.adapter.index(row, col)
                value = getattr(self.model[row], ('x', 'y', 'z')[col])
                adapter_value = self.adapter.data(index, PythonObjectRole)
                self.assertEqual(adapter_value, value,
                    'test_model_insertion failed')


class ObjectTreeAdapterTestCase(unittest.TestCase):

    def setUp(self):

        def build_level(level, parent, prefix):
            model = ObservableListProxy()
            for i in range(0, random.randint(3, 7)):
                o = TestObject()
                o.parent = parent
                o.x = u'x{0}{1}'.format(prefix, i)
                o.y = u'y{0}{1}'.format(prefix, i)
                o.z = u'z{0}{1}'.format(prefix, i)
                model.append(o)
                if level < 3:
                    o.children = build_level(level + 1, o, prefix + str(i))
                elif i == 1:  # Test with and without attribute
                    o.children = None
            return model

        self.model = build_level(0, None, '')

        self.adapter = ObjectTreeAdapter(
            ('x', 'y', 'z'),
            self.model,
            TestObject, rootless=True,
            options=set(['edit']))

    def test_rows_columns(self):

        def test_level(submodel, parent):
            self.assertEqual(self.adapter.rowCount(parent), len(submodel))
            self.assertEqual(self.adapter.columnCount(parent), 3,
                'ObjectListAdapter.columnCount must return 3')
            for row in range(0, len(submodel)):
                try:
                    if submodel[row].children is not None:
                        test_level(submodel[row].children,
                            self.adapter.index(row, 0, parent))
                except AttributeError:
                    pass

        test_level(self.model, QtCore.QModelIndex())

    def test_indexes(self):

        def test_level(submodel, parent):
            for row in range(-1, len(submodel) + 1):
                for col in range(-1, 4):
                    index = self.adapter.index(row, col, parent)
                    if row in (-1, len(submodel)) or col in (-1, 3):
                        self.assertFalse(index.isValid(),
                            ('ObjectTreeAdapter.index({0},{1})) should be'
                            ' invalid').format(row, col))
                    else:
                        self.assertEqual(index.row(), row,
                            'ObjectTreeAdapter.index({0}, {1}) has wrong row'
                            .format(row, col))
                        self.assertEqual(index.column(), col,
                            'ObjectTreeAdapter.index({0}, {1}) has wrong column'
                            .format(row, col))

            for row in range(0, len(submodel)):
                try:
                    if submodel[row].children is not None:
                        test_level(submodel[row].children,
                            self.adapter.index(row, 0, parent))
                except AttributeError:
                    pass

        test_level(self.model, QtCore.QModelIndex())

    def test_data(self):

        def test_level(submodel, parent):
            for row in range(-1, len(submodel) + 1):
                for col in range(-1, 4):
                    index = self.adapter.index(row, col, parent)
                    if row in (-1, len(submodel)) or col in (-1, 3):
                        value = None
                    else:
                        value = getattr(submodel[row], ('x', 'y', 'z')[col])
                    adapter_value = self.adapter.data(index)
                    self.assertEqual(adapter_value, value,
                        'ObjectTreeAdapter.data on index({0}, {1}) failed'
                            .format(row, col))

            for row in range(-1, len(submodel) + 1):
                for col in range(-1, 4):
                    index = self.adapter.index(row, col, parent)
                    if row in (-1, len(submodel)) or col in (-1, 3):
                        value = None
                    else:
                        value = getattr(submodel[row], ('x', 'y', 'z')[col])
                    if col == 0 and value is not None:
                        value = value.upper()
                    adapter_value = self.adapter.data(index, Qt.EditRole)
                    self.assertEqual(adapter_value, value,
                        'ObjectListAdapter.data on index({0}, {1}) failed'
                            .format(row, col))

            for row in range(-1, len(submodel) + 1):
                for col in range(-1, 4):
                    index = self.adapter.index(row, col, parent)
                    if row in (-1, len(submodel)) or col in (-1, 3):
                        value = None
                    else:
                        value = Qt.AlignCenter if col == 1 else None

                    adapter_value = self.adapter.data(index,
                        Qt.TextAlignmentRole)
                    self.assertEqual(adapter_value, value,
                        'ObjectListAdapter.data on index({0}, {1}) failed'
                            .format(row, col))

            for row in range(0, len(submodel)):
                try:
                    if submodel[row].children is not None:
                        test_level(submodel[row].children,
                            self.adapter.index(row, 0, parent))
                except AttributeError:
                    pass

        test_level(self.model, QtCore.QModelIndex())

    def test_setData(self):

        def test_level(submodel, parent):
            print "before", submodel
            for row in range(-1, len(submodel) + 1):
                for col in range(-1, 4):
                    index = self.adapter.index(row, col, parent)
                    value = chr(random.randint(65, 90)) + str(row)
                    expected = (False if row in (-1, len(submodel))
                        or col in (-1, 3) else True)
                    r = self.adapter.setData(index, value)
                    self.assertEqual(r, expected,
                        ('ObjectListAdapter.setData on index({0}, {1}) failed'
                        'must return {2}')
                        .format(row, col, expected))
                    if r:
                        model_value = getattr(submodel[row],
                            ('x', 'y', 'z')[col])
                        self.assertEqual(model_value, value,
                        'ObjectListAdapter.setData on index({0}, {1}) failed'
                        .format(row, col))
            print "after", submodel
            for row in range(0, len(submodel)):
                try:
                    if submodel[row].children is not None:
                        test_level(submodel[row].children,
                            self.adapter.index(row, 0, parent))
                except AttributeError:
                    pass

        test_level(self.model, QtCore.QModelIndex())

    def test_flags(self):

        def test_level(submodel, parent):
            for row in range(-1, len(submodel) + 1):
                for col in range(-1, 4):
                    index = self.adapter.index(row, col, parent)
                    flags = self.adapter.flags(index)
                    if row < 0 or row > len(submodel) - 1 or col < 0 or col > 2:
                        expected = Qt.NoItemFlags
                    elif col == 0:
                        expected = Qt.ItemIsEnabled
                    else:
                        expected = (Qt.ItemIsSelectable | Qt.ItemIsEditable
                            | Qt.ItemIsEnabled)
                    self.assertEqual(flags, expected,
                        'ObjectTreeAdapter.flags() on index {0},{1}'
                        .format(row, col))

            for row in range(0, len(submodel)):
                try:
                    if submodel[row].children is not None:
                        test_level(submodel[row].children,
                            self.adapter.index(row, 0, parent))
                except AttributeError:
                    pass

        test_level(self.model, QtCore.QModelIndex())


if __name__ == '__main__':
    unittest.main()
