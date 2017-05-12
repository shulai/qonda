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

from .. import PYQT_VERSION
if PYQT_VERSION == 5:
    from PyQt5 import QtCore, QtGui, QtWidgets
    from PyQt5.QtCore import Qt, pyqtSignal
else:
    from PyQt4 import QtCore, QtGui  # lint:ok
    from PyQt4.QtCore import Qt, pyqtSignal  # lint:ok
    QtWidgets = QtGui
from ..icons import icons_rc  # lint:ok


PythonObjectRole = 32


class LookupWidgetDelegate(QtWidgets.QStyledItemDelegate):

    def __init__(self, parent=None, search_function=None, search_window=None,
            display_formatter=unicode):
        QtWidgets.QItemDelegate.__init__(self, parent)
        self.search_function = search_function
        self.search_window = search_window
        self.display_formatter = display_formatter
        self._setting_model_data = False

    def createEditor(self, parent, option, index):
        editor = LookupWidget(parent)
        editor.search_function = self.search_function
        editor.search_window = self.search_window
        editor.display_formatter = self.display_formatter
        return editor

    def setSearchWindow(self, window):
        self.search_window = window

    def setEditorData(self, editor, index):
        # Avoid setting editor data inside a setModelData call
        # This happens when ObjectListAdapter inserts the first row
        # and the blank value of the new row is sent into the editor
        # Hope doesn't cause any regressions in other cases.
        if  self._setting_model_data:
            return
        editor.setValue(index.data(role=PythonObjectRole))
        editor.valueChanged.connect(self.widgetValueChanged)

    def setModelData(self, editor, model, index):
        self._setting_model_data = True
        model.setData(index, editor.value(), role=PythonObjectRole)
        self._setting_model_data = False

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def widgetValueChanged(self):
        self.commitData.emit(self.sender())


class LookupWidget(QtWidgets.QLineEdit):
    """
        Widget to search object using an user provided search string

        After creating the widget, must set the search_function attribute
        with a callable that receives a string and returns a list of matching
        objects
    """
    _mappingDelegateClass = LookupWidgetDelegate

    valueChanged = pyqtSignal()

    def __init__(self, parent=None):
        QtWidgets.QLineEdit.__init__(self, parent)
        self.editingFinished.connect(self._search_and_end)

        self.button = QtWidgets.QToolButton(self)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        icon1 = QtGui.QIcon(":/qonda/lookup.png")
        self.button.setIcon(icon1)
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.clicked.connect(self.openSearchWindow)
        self.button.resize(18, 18)
        self.button.hide()

        self.menu = QtWidgets.QMenu(self)
        self.placeholder = None
        self._value = None

        self.search_function = True
        self.search_window = None
        self.on_value_set = None
        self._editing = False
        self.display_formatter = unicode
        self._show_value()

    def resizeEvent(self, event):
        self.button.move(self.rect().right() - 19,
            (self.height() - self.button.height()) / 2)
        super(LookupWidget, self).resizeEvent(event)

    #def focusOutEvent(self, event):
        #if self._editing:
            #self._search_value()
            #self._edit_finished()
        #super(LookupWidget, self).focusOutEvent(event)

    def mousePressEvent(self, event):
        self.selectAll()
        event.accept()

    def keyPressEvent(self, event):
        if self.isReadOnly():
            event.accept()
            return
        if self._editing:
            if event.key() == Qt.Key_Escape:
                self._show_value()
                self._edit_finished()
            else:
                super(LookupWidget, self).keyPressEvent(event)
            return
        # Avoid Enter and dead keys events erasing the text
        if event.text().strip() == '':
            return
        self._edit()
        super(LookupWidget, self).keyPressEvent(event)

    def value(self):
        if self._editing:
            self._search_value()
        return self._value

    def setValue(self, value):
        if value == self._value:
            return
        if self.on_value_set is not None:
            value = self.on_value_set(value)
        self._value = value
        if self._editing:
            self._edit_finished()
        self._show_value()
        self.valueChanged.emit()

    def clear(self):
        self.setValue(None)

    def _edit(self):
        self.setText('')
        self._editing = True
        if self.search_window:
            # Workaround: setting padding-right only seems to set other
            # paddings to zero. Not sure if 2px works ok in every style
            # and platform
            self.setStyleSheet('padding: 2px 20px 2px 2px')
            self.button.show()

    def _search_and_end(self):
        if self._editing:
            if self._search_value():
                self._edit_finished()

    def _edit_finished(self):
        self._editing = False
        if self.search_window:
            self.setStyleSheet('')
            self.button.hide()

    def _show_value(self):
        if self._value is None:
            super(LookupWidget, self).clear()
        else:
            self.setText(self.display_formatter(self._value))
            # When the value representation is wider than the widget,
            # the leftmost part must be visible
            self.setCursorPosition(0)

    def _search_value(self):
        text = self.text()
        if text == '':
            self.setValue(None)
            return True

        values = self.search_function(text)
        if len(values) == 0:
            self.setFocus()
            self.selectAll()
            return False  # Nothing found, back to editing
        elif len(values) == 1:
            self.setValue(values[0])
            return True
        else:
            actions = {}
            self.menu.clear()
            for i, value in enumerate(values):
                action = self.menu.addAction(self.display_formatter(value))
                actions[action] = i
                if i == 0:
                    self.menu.setActiveAction(action)
            action = self.menu.exec_(self.mapToGlobal(QtCore.QPoint(0,
                self.size().height())))
            if action:
                self.setValue(values[actions[action]])
                return True
            else:
                self.setFocus()
                return False  # Nothing found, back to editing

    @QtCore.pyqtSlot()
    def openSearchWindow(self):
        if self.search_window:
            self.search_window.setWindowModality(Qt.ApplicationModal)
            self.search_window.closeEvent = self.searchWindowCloseEvent
            self.search_window.show()

    def searchWindowCloseEvent(self, event):
        value = self.search_window.value()
        if value:
            self.setValue(value)
