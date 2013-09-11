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

import sys
import datetime
from PyQt4 import QtGui
from PyQt4.QtCore import Qt

from qonda.widgets import widgets

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
        except ValueError:
            v = index.data(role=PythonObjectRole)
            if v is None:  # Set first element if no value present
                try:
                    editor.setCurrentIndex(-1 if editor.allowEmpty else 0)
                except AttributeError:  # if not qonda but regular QComboBox
                    editor.setCurrentIndex(0)
            else:
                raise ValueError('Value "{0}" not present in QComboBox model!'
                    .format(index.data(role=PythonObjectRole)))
        except AttributeError as e:
            if sys.version_info.major == 3:
                new_e = TypeError('Invalid QComboBox model {0}. Did you assign'
                    ' a Qonda Model?\nHint: Value {1}'.format(editor.model(),
                    index.data(role=PythonObjectRole)))
                new_e.__cause__ = e
                raise new_e
            else:
                raise TypeError('Invalid QComboBox model {0}. Did you assign'
                    ' a Qonda Model?'.format(editor.model()))

    def setModelData(self, editor, model, index):
        try:
            value = editor.model()._model[editor.currentIndex()]
        except AttributeError as e:
            if sys.version_info.major == 3:
                new_e = TypeError('Invalid QComboBox model {0}. Did you assign'
                    ' a Qonda Model?'.format(editor.model()))
                new_e.__cause__ = e
                raise new_e
            else:
                raise TypeError('Invalid QComboBox model {0}. Did you assign'
                    ' a Qonda Model?'.format(editor.model()))

        model.setData(index, value, role=PythonObjectRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class DateEditDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = widgets.DateEdit(parent)
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
        date = index.model().data(index, PythonObjectRole)
        if date:
            editor.setDate(date)
        else:
            editor.clear()


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
        value = index.data(Qt.EditRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, str(editor.text()), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class CheckBoxDelegate(QtGui.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtGui.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtGui.QCheckBox(parent)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(PythonObjectRole)
        editor.setChecked(value)

    def setModelData(self, editor, model, index):
        model.setData(index, bool(editor.isChecked()), PythonObjectRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, options, index):
        value = index.data(PythonObjectRole)
        painter.save()
        style = QtGui.QApplication.style()
        #self.drawBackground(painter, options, index)
        opt = QtGui.QStyleOptionButton()
        opt.state |= QtGui.QStyle.State_On if value else QtGui.QStyle.State_Off
        opt.state |= QtGui.QStyle.State_Enabled
        #opt.text = text
        checkbox_rect = style.subElementRect(QtGui.QStyle.SE_CheckBoxIndicator,
            opt)
        opt.rect = options.rect
        opt.rect.setLeft(options.rect.x() + options.rect.width() / 2
            - checkbox_rect.width() / 2)
        style.drawControl(QtGui.QStyle.CE_CheckBox, opt, painter)
        painter.restore()
