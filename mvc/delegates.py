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

from .. import PYQT_VERSION
if PYQT_VERSION == 5:
    from PyQt5 import QtGui
    from PyQt5.QtCore import Qt
else:
    from PyQt4 import QtGui  # lint:ok
    from PyQt4.QtCore import Qt  # lint:ok
    QtWidgets = QtGui

from ..widgets import widgets

PythonObjectRole = 32


class SpinBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = widgets.SpinBox(parent)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        value = int(index.model().data(index, Qt.EditRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        value = editor.value()
        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)


class ComboBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, model=None, **properties):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.model = model
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = widgets.ComboBox(parent)
        if self.model:
            editor.setModel(self.model)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        try:
            editor.setCurrentIndex(editor.model()
                .getPyModel().index(index.data(role=PythonObjectRole)))
        except ValueError:
            v = index.data(role=PythonObjectRole)
            if v is None:  # Set first element if no value present
                try:
                    editor.setCurrentIndex(-1 if editor.allowEmpty else 0)
                except AttributeError:  # if not qonda but regular QComboBox
                    editor.setCurrentIndex(0)
            else:
                raise ValueError(
                    'Value "{0}" not present in {1} QComboBox model!'
                    .format(index.data(role=PythonObjectRole),
                        editor.objectName()))
        except AttributeError as e:
            if sys.version_info.major == 3:
                new_e = TypeError('Invalid QComboBox model {0} for {1}. '
                    'Did you assign a Qonda Model?\nHint: Value {2}'
                    .format(editor.model(),
                        editor.objectName(),
                        index.data(role=PythonObjectRole)))
                new_e.__cause__ = e
                raise new_e
            else:
                raise TypeError('Invalid QComboBox model {0} for {1}. '
                    'Did you assign a Qonda Model?'
                    .format(editor.model(), editor.objectName()))

    def setModelData(self, editor, model, index):
        try:
            value = editor.model().getPyModel()[editor.currentIndex()]
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


class DateEditDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
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


class LineEditDelegate(QtWidgets.QStyledItemDelegate):
    """
        Specialized delegate what brings a customizable LineEdit editor
        Allowed properties:
            inputMask
            validator
            maxLength
            alignment
    """
    def __init__(self, parent=None, validator=None, **properties):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.validator = validator
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QLineEdit(parent)
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


class CheckBoxDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = QtWidgets.QCheckBox(parent)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        return editor

    def setEditorData(self, editor, index):
        value = index.data(PythonObjectRole)
        editor.setChecked(bool(value))

    def setModelData(self, editor, model, index):
        model.setData(index, bool(editor.isChecked()), PythonObjectRole)

    def updateEditorGeometry(self, editor, option, index):
        style = QtWidgets.QApplication.style()
        checkbox_rect = style.subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, option)
        rect = option.rect
        x = option.rect.x() + (option.rect.width() - checkbox_rect.width()) / 2
        rect.setLeft(x)
        rect.setWidth(checkbox_rect.width())
        editor.setGeometry(rect)

    def paint(self, painter, options, index):
        value = index.data(PythonObjectRole)
        painter.save()
        style = QtWidgets.QApplication.style()
        #self.drawBackground(painter, options, index)
        opt = QtWidgets.QStyleOptionButton()
        opt.state |= (QtWidgets.QStyle.State_On if value
            else QtWidgets.QStyle.State_Off)
        opt.state |= QtWidgets.QStyle.State_Enabled
        #opt.text = text
        checkbox_rect = style.subElementRect(
            QtWidgets.QStyle.SE_CheckBoxIndicator, opt)
        opt.rect = options.rect
        opt.rect.setLeft(options.rect.x() + options.rect.width() / 2
            - checkbox_rect.width() / 2)
        style.drawControl(QtWidgets.QStyle.CE_CheckBox, opt, painter)
        painter.restore()


class NumberEditDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, **properties):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.__properties = properties

    def createEditor(self, parent, option, index):
        editor = widgets.NumberEdit(parent)
        for prop_name, prop_value in self.__properties.iteritems():
            editor.setProperty(prop_name, prop_value)
        editor.selectAll()
        return editor

    def setEditorData(self, editor, index):
        value = index.data(PythonObjectRole)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.getValue(), PythonObjectRole)


class PixmapDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, scale=False):
        QtWidgets.QStyledItemDelegate.__init__(self, parent)
        self.__scale = scale

    def paint(self, painter, options, index):
        pixmap = index.data()
        if pixmap is not None:
            painter.save()
            if self.__scale:
                painter.drawPixmap(options.rect, pixmap)
            else:
                painter.drawPixmap(options.rect.topLeft(), pixmap)
            painter.restore()
