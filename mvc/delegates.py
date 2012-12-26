# -*- coding: utf-8 -*-

#   This file is part of Qonda.
#
#    Qonda is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Qonda is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Qonda; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


import datetime
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

PythonObjectRole = 32


class SpinBoxDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtGui.QSpinBox(parent)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        value = int(index.model().data(index, Qt.EditRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        model.setData(index, editor.value(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ComboBoxDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None, model=None, **properties):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.model = model
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtGui.QComboBox(parent)
        if self.model:
            editor.setModel(self.model)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        try:
            editor.setCurrentIndex(editor.model().
                _model.index(index.data(role=PythonObjectRole)))
        except AttributeError:
            raise TypeError('Invalid QComboBox model. Did you assign a '
                'Qonda Model?')

    def setModelData(self, editor, model, index):
        try:
            value = editor.model()._model[editor.currentIndex()]
        except AttributeError:
            raise TypeError('Invalid QComboBox model. Did you assign a '
                'Qonda Model?')

        model.setData(index, value, role=PythonObjectRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DateEditDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtGui.QDateEdit(parent)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setModelData(self, editor, model, index):
        # PyQt authors like QDate more than datetime.date, setapi doesn't work
        date = editor.date().toPyDate()
        if date == datetime.date(1752, 9, 14):
            date = None
        model.setData(index, date, Qt.EditRole)

    def setEditorData(self, editor, index):
        date = int(index.model().data(index, Qt.EditRole))
        if not date:
            date = datetime.date(1752, 9, 14)
        editor.setDate(date)


class LineEditDelegate(QtGui.QStyledItemDelegate):
    """
        Specialized delegate what brings a customizable LineEdit editor
        Allowed properties:
            inputMask
            validator
            maxLength
            alignment
    """
    def __init__(self, parent=None, validator=None, **properties):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.validator = validator
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtGui.QLineEdit(parent)
        if self.validator:
            editor.setValidator(self.validator)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, str(editor.text()), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


