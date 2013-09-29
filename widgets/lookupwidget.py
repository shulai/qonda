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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt
from ..icons import icons_rc


PythonObjectRole = 32


class LookupWidgetDelegate(QtGui.QItemDelegate):

    def __init__(self, parent=None, search_function=None, search_window=None):
        QtGui.QItemDelegate.__init__(self, parent)
        self.search_function = search_function
        self.search_window = search_window

    def createEditor(self, parent, option, index):
        editor = LookupWidget(parent)
        editor.search_function = self.search_function
        editor.search_window = self.search_window
        return editor

    def setSearchWindow(self, window):
        self.search_window = window

    def setEditorData(self, editor, index):
        editor.setValue(index.data(role=PythonObjectRole))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value(), role=PythonObjectRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

    def paint(self, painter, options, index):
        try:
            model = index.model().data(index, Qt.EditRole)
            value = unicode(model)
        except AttributeError:
            value = ''

        painter.save()
        self.drawBackground(painter, options, index)
        # if not options edicion
        self.drawDisplay(painter, options, options.rect, value)
        painter.restore()


class LookupWidget(QtGui.QLineEdit):
    """
        Widget to search object using an user provided search string

        After creating the widget, must set the search_function attribute
        with a callable that receives a string and returns a list of matching
        objects
    """
    _mappingDelegateClass = LookupWidgetDelegate

    def __init__(self, parent=None):
        QtGui.QLineEdit.__init__(self, parent)
        self.editingFinished.connect(self._search_value)

        self.button = QtGui.QToolButton(self)
        self.button.setFocusPolicy(Qt.NoFocus)
        self.button.setCursor(QtCore.Qt.ArrowCursor)
        icon1 = QtGui.QIcon(":/icons/lookup.png")
        self.button.setIcon(icon1)
        self.button.setStyleSheet('border: 0px; padding: 0px;')
        self.button.clicked.connect(self.openSearchWindow)
        self.button.resize(18, 18)
        self.button.hide()

        self.menu = QtGui.QMenu(self)
        self.placeholder = None
        self._value = None

        self.search_function = True
        self.search_window = None
        self._editing = False
        self._show_value()

    def resizeEvent(self, event):
        self.button.move(self.rect().right() - 19, 
            (self.height() - self.button.height()) / 2)
        super(LookupWidget, self).resizeEvent(event)

    def focusOutEvent(self, event):
        if self._editing:
            self._search_value()
            self._edit_finished()
        super(LookupWidget, self).focusOutEvent(event)

    def mousePressEvent(self, event):
        self._edit()

    def keyPressEvent(self, event):
        if self._editing:
            if event.key() == Qt.Key_Escape:
                self._show_value()
                self._edit_finished()
            else:
                super(LookupWidget, self).keyPressEvent(event)
            return
        if event.text() == '':  # Avoid dead keys events erasing the text
            return
        self._edit()
        super(LookupWidget, self).keyPressEvent(event)

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = value
        if self._editing:
            self._edit_finished()
        self._show_value()

    def _edit(self):
        self.setText('')
        self._editing = True
        if self.search_window:
            # Workaround: setting padding-right only seems to set other
            # paddings to zero. Not sure if 2px works ok in every style
            # and platform
            self.setStyleSheet('padding: 2px 20px 2px 2px')
            self.button.show()

    def _edit_finished(self):
        self._editing = False
        if self.search_window:
            self.setStyleSheet('')
            self.button.hide()

    def _show_value(self):
        if self._value is None:
            self.clear()
        else:
            self.setText(unicode(self._value))

    def _search_value(self):
        text = self.text()
        if text == '':
            self.setValue(None)
            return

        values = self.search_function(text)
        if len(values) == 0:
            self.setFocus()
            return  # Nothing found, back to editing
        elif len(values) == 1:
            self.setValue(values[0])
        else:
            actions = {}
            self.menu.clear()
            for i, value in enumerate(values):
                action = self.menu.addAction(unicode(value))
                actions[action] = i
                if i == 0:
                    self.menu.setActiveAction(action)
            action = self.menu.exec_(self.mapToGlobal(QtCore.QPoint(0,
                self.size().height())))
            if action:
                self.setValue(values[actions[action]])
            else:
                self.setFocus()
            return  # Nothing found, back to editing

    @QtCore.pyqtSignature("")
    def openSearchWindow(self):
        if self.search_window:
            self.search_window.setWindowModality(Qt.ApplicationModal)
            self.search_window.closeEvent = self.searchWindowCloseEvent
            print "open"
            self.search_window.show()
            
    def searchWindowCloseEvent(self, event):
        value = self.search_window.value()
        if value:
            self.setValue(value)

